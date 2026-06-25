import asyncio
import json
import os
import random
import time
from pathlib import Path

from aiohttp import WSMsgType, web


LOBBY_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ROOT = Path(__file__).parent
WEB_DIR = ROOT / "web"
ROOMS = {}


def new_code():
    return "".join(random.choice(LOBBY_CHARS) for _ in range(5))


class Room:
    def __init__(self, code, settings, prompt):
        self.code = code
        self.settings = dict(settings)
        self.prompt = prompt
        self.clients = {}
        self.next_player_id = 0
        self.started = False
        self.current_turn = 0
        self.current_round = 1
        self.assignments = []
        self.contributions = []
        self.turn_started_at = 0.0
        self.lock = asyncio.Lock()
        self.timer_task = asyncio.create_task(self.timer_loop())

    def player_names(self):
        count = int(self.settings.get("player_count", 4))
        names = []
        for player_id in sorted(self.clients):
            if len(names) < count:
                names.append(self.clients[player_id]["name"])
        while len(names) < count:
            names.append(f"Player {len(names) + 1}")
        return names

    async def send(self, ws, message):
        await ws.send_str(json.dumps(message, separators=(",", ":")))

    async def broadcast(self, message):
        dead = []
        for player_id, client in list(self.clients.items()):
            try:
                await self.send(client["ws"], message)
            except ConnectionResetError:
                dead.append(player_id)
        for player_id in dead:
            self.clients.pop(player_id, None)

    async def broadcast_lobby(self):
        await self.broadcast({
            "type": "lobby",
            "lobby_code": self.code,
            "players": self.player_names(),
            "connected_count": len(self.clients),
            "settings": self.settings,
            "prompt": self.prompt,
        })

    async def add_client(self, ws, name):
        async with self.lock:
            player_id = self.next_player_id
            self.next_player_id += 1
            self.clients[player_id] = {
                "ws": ws,
                "name": (name or "Player").strip()[:16] or "Player",
            }
            await self.send(ws, {
                "type": "welcome",
                "player_id": player_id,
                "lobby_code": self.code,
                "settings": self.settings,
                "prompt": self.prompt,
            })
            await self.broadcast_lobby()
            return player_id

    async def remove_client(self, player_id):
        async with self.lock:
            self.clients.pop(player_id, None)
            await self.broadcast_lobby()
            if not self.clients and not self.started:
                ROOMS.pop(self.code, None)
                self.timer_task.cancel()

    async def handle_message(self, player_id, message):
        async with self.lock:
            message_type = message.get("type")
            if message_type == "settings" and player_id == 0 and not self.started:
                self.settings.update(message.get("settings", {}))
                await self.broadcast_lobby()
            elif message_type == "prompt" and player_id == 0 and not self.started:
                self.prompt = message.get("prompt", self.prompt)
                await self.broadcast_lobby()
            elif message_type == "start_game" and player_id == 0 and not self.started:
                await self.start_game_locked()
            elif message_type == "stroke" and self.started and player_id == self.current_turn:
                stroke = dict(message)
                stroke["sender_id"] = player_id
                stroke["canvas_index"] = self.assignments[self.current_turn]
                await self.broadcast(stroke)
            elif message_type == "end_turn" and self.started and player_id == self.current_turn:
                await self.finish_turn_locked()

    async def start_game_locked(self):
        self.started = True
        self.current_turn = 0
        self.current_round = 1
        player_count = int(self.settings.get("player_count", 4))
        self.assignments = [0 for _ in range(player_count)]
        self.contributions = [[]]
        self.turn_started_at = time.monotonic()
        await self.broadcast({
            "type": "start_game",
            "lobby_code": self.code,
            "settings": self.settings,
            "prompt": self.prompt,
            "player_names": self.player_names(),
        })
        await self.broadcast_turn()

    async def finish_turn_locked(self):
        player_names = self.player_names()
        canvas_index = 0
        player_name = player_names[self.current_turn]
        if player_name not in self.contributions[canvas_index]:
            self.contributions[canvas_index].append(player_name)

        self.current_turn += 1
        player_count = int(self.settings.get("player_count", 4))
        if self.current_turn >= player_count:
            self.current_turn = 0
            self.current_round += 1
            if self.current_round > int(self.settings.get("total_rounds", 4)):
                self.started = False
                await self.broadcast({
                    "type": "gallery",
                    "contributions": self.contributions,
                })
                return

        self.turn_started_at = time.monotonic()
        await self.broadcast_turn()

    async def broadcast_turn(self):
        await self.broadcast({
            "type": "turn",
            "current_turn": self.current_turn,
            "current_round": self.current_round,
            "assignments": self.assignments,
            "turn_started_at": time.time(),
            "contributions": self.contributions,
        })

    async def timer_loop(self):
        while True:
            await asyncio.sleep(0.05)
            async with self.lock:
                if not self.started:
                    continue
                seconds = int(self.settings.get("round_seconds", 30))
                if time.monotonic() - self.turn_started_at >= seconds:
                    await self.finish_turn_locked()


async def index(_request):
    return web.FileResponse(WEB_DIR / "index.html")


async def health(_request):
    return web.json_response({
        "ok": True,
        "rooms": len(ROOMS),
        "websocket_path": "/ws",
    })


async def websocket_handler(request):
    ws = web.WebSocketResponse(max_msg_size=4_000_000, heartbeat=15)
    await ws.prepare(request)
    room = None
    player_id = None

    try:
        first = await ws.receive_json()
        message_type = first.get("type")
        if message_type == "create_room":
            code = (first.get("room_code") or new_code()).upper()[:5]
            while code in ROOMS:
                code = new_code()
            room = Room(code, first.get("settings", {}), first.get("prompt", ""))
            ROOMS[code] = room
        elif message_type == "join_room":
            code = (first.get("room_code") or "").upper()[:5]
            room = ROOMS.get(code)
            if room is None:
                await ws.send_json({"type": "error", "message": f"Room {code} not found"})
                return ws
        else:
            await ws.send_json({"type": "error", "message": "Expected create_room or join_room"})
            return ws

        player_id = await room.add_client(ws, first.get("name"))
        async for message in ws:
            if message.type == WSMsgType.TEXT:
                await room.handle_message(player_id, json.loads(message.data))
            elif message.type == WSMsgType.ERROR:
                break
    finally:
        if room is not None and player_id is not None:
            await room.remove_client(player_id)
    return ws


def make_app():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/static", WEB_DIR)
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    web.run_app(make_app(), host="0.0.0.0", port=port)
