import asyncio
import json
import queue
import threading

import websockets


DEFAULT_WS_URL = "ws://localhost:8765"


class NetworkClient:
    def __init__(self):
        self.inbox = queue.SimpleQueue()
        self.outbox = queue.SimpleQueue()
        self.connected = False
        self.player_id = None
        self.status = ""
        self.loop = None
        self.websocket = None

    def connect(self, url, room_code, name, create_room=False, settings=None, prompt=None):
        if self.connected:
            return
        threading.Thread(
            target=self._thread_main,
            args=(url, room_code, name, create_room, settings or {}, prompt or ""),
            daemon=True,
        ).start()

    def send(self, message):
        if not self.connected:
            return
        self.outbox.put(dict(message))

    def close(self):
        if self.connected:
            self.outbox.put(None)

    def _thread_main(self, url, room_code, name, create_room, settings, prompt):
        asyncio.run(self._run(url, room_code, name, create_room, settings, prompt))

    async def _run(self, url, room_code, name, create_room, settings, prompt):
        try:
            async with websockets.connect(url, ping_interval=15, ping_timeout=15, max_size=4_000_000) as websocket:
                self.websocket = websocket
                self.connected = True
                hello = {
                    "type": "create_room" if create_room else "join_room",
                    "room_code": room_code,
                    "name": name,
                    "settings": settings,
                    "prompt": prompt,
                }
                await websocket.send(json.dumps(hello, separators=(",", ":")))
                sender = asyncio.create_task(self._send_loop(websocket))
                receiver = asyncio.create_task(self._recv_loop(websocket))
                done, pending = await asyncio.wait(
                    [sender, receiver],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                for task in done:
                    task.result()
        except Exception as exc:
            self.inbox.put({"type": "error", "message": str(exc)})
        finally:
            self.connected = False
            self.websocket = None
            self.inbox.put({"type": "disconnect"})

    async def _send_loop(self, websocket):
        while True:
            message = await asyncio.to_thread(self.outbox.get)
            if message is None:
                await websocket.close()
                return
            await websocket.send(json.dumps(message, separators=(",", ":")))

    async def _recv_loop(self, websocket):
        async for raw in websocket:
            message = json.loads(raw)
            if message.get("type") == "welcome":
                self.player_id = message.get("player_id")
            self.inbox.put(message)
