import asyncio
from typing import Any, Dict

from aiohttp import web
from stats import StatCollector


class WebSocketStatsBroadcaster:
    def __init__(self, collector: StatCollector):
        self._collector = collector
        self._clients = set()

    def add_client(self, websocket: web.WebSocketResponse):
        self._clients.add(websocket)

    def remove_client(self, websocket: web.WebSocketResponse):
        self._clients.discard(websocket)

    def remove_all_clients(self):
        self._clients.clear()

    async def _send_json(self, websocket: web.WebSocketResponse, message):
        try:
            await websocket.send_json(message)
        except ConnectionResetError:
            self.remove_client(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        if self._clients:
            tasks = [self._send_json(websocket, message) for websocket in self._clients]
            await asyncio.gather(*tasks)

    async def run(self, delay: int = 1):
        while True:
            data = self._collector.get_stats()
            await self.broadcast_json(data)
            await asyncio.sleep(delay)
