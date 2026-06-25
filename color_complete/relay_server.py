import asyncio
import json
import os
import random
import socket
import string
import time

import websockets


LOBBY_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ROOMS = {}


def new_code():
    return "".join(random.choice(LOBBY_CHARS) for _ in range(5))


async def send_json(websocket, message):
    await websocket.send(json.dumps(message, separators=(",", ":")))


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

    def player_names(self):
        count = int(self.settings.get("player_count", 4))
        names = []
        for player_id in sorted(self.clients):
            if len(names) < count:
                names.append(self.clients[player_id]["name"])
        while len(names) < count:
            names.append(f"Player {len(names) + 1}")
        return names

    async def broadcast(self, message):
        dead = []
        for player_id, client in list(self.clients.items()):
            try:
                await send_json(client["websocket"], message)
            except websockets.ConnectionClosed:
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

    async def add_client(self, websocket, name):
        async with self.lock:
            player_id = self.next_player_id
            self.next_player_id += 1
            self.clients[player_id] = {
                "websocket": websocket,
                "name": (name or "Player").strip()[:16] or "Player",
            }
            await send_json(websocket, {
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
                await self.start_game()
            elif message_type == "stroke" and self.started and player_id == self.current_turn:
                stroke = dict(message)
                stroke["sender_id"] = player_id
                stroke["canvas_index"] = self.assignments[self.current_turn]
                await self.broadcast(stroke)
            elif message_type == "undo" and self.started and player_id == self.current_turn:
                undo = dict(message)
                undo["sender_id"] = player_id
                undo["canvas_index"] = self.assignments[self.current_turn]
                await self.broadcast(undo)
            elif message_type == "end_turn" and self.started and player_id == self.current_turn:
                await self.finish_turn()

    async def start_game(self):
        self.started = True
        self.current_turn = 0
        self.current_round = 1
        player_count = int(self.settings.get("player_count", 4))
        self.assignments = list(range(player_count))
        self.contributions = [[] for _ in range(player_count)]
        self.turn_started_at = time.monotonic()
        await self.broadcast({
            "type": "start_game",
            "lobby_code": self.code,
            "settings": self.settings,
            "prompt": self.prompt,
            "player_names": self.player_names(),
        })
        await self.broadcast_turn()

    async def finish_turn(self):
        player_names = self.player_names()
        canvas_index = self.assignments[self.current_turn]
        player_name = player_names[self.current_turn]
        if player_name not in self.contributions[canvas_index]:
            self.contributions[canvas_index].append(player_name)
        self.current_turn += 1
        player_count = int(self.settings.get("player_count", 4))
        if self.current_turn >= player_count:
            self.current_turn = 0
            self.current_round += 1
            self.assignments = self.assignments[-1:] + self.assignments[:-1]
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
                    await self.finish_turn()


async def handler(websocket):
    room = None
    player_id = None
    try:
        first = json.loads(await websocket.recv())
        message_type = first.get("type")
        if message_type == "create_room":
            code = (first.get("room_code") or new_code()).upper()[:5]
            while code in ROOMS:
                code = new_code()
            room = Room(code, first.get("settings", {}), first.get("prompt", ""))
            ROOMS[code] = room
            asyncio.create_task(room.timer_loop())
        elif message_type == "join_room":
            code = (first.get("room_code") or "").upper()[:5]
            room = ROOMS.get(code)
            if room is None:
                await send_json(websocket, {"type": "error", "message": f"Room {code} not found"})
                return
        else:
            await send_json(websocket, {"type": "error", "message": "Expected create_room or join_room"})
            return

        player_id = await room.add_client(websocket, first.get("name"))
        async for raw in websocket:
            await room.handle_message(player_id, json.loads(raw))
    except websockets.ConnectionClosed:
        pass
    except json.JSONDecodeError:
        pass
    finally:
        if room is not None and player_id is not None:
            await room.remove_client(player_id)
            if not room.clients and not room.started:
                ROOMS.pop(room.code, None)


async def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8765"))
    async with websockets.serve(handler, host, port, ping_interval=15, ping_timeout=15, max_size=4_000_000):
        print(f"Color Complete WebSocket relay listening on ws://{host}:{port}", flush=True)
        for address in local_addresses():
            print(f"LAN clients can use: ws://{address}:{port}", flush=True)
        await asyncio.Future()


def local_addresses():
    addresses = set()
    hostname = socket.gethostname()
    try:
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            address = info[4][0]
            if not address.startswith("127."):
                addresses.add(address)
    except socket.gaierror:
        pass

    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        addresses.add(probe.getsockname()[0])
    except OSError:
        pass
    finally:
        probe.close()

    return sorted(addresses)


if __name__ == "__main__":
    asyncio.run(main())
