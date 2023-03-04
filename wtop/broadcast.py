import asyncio
from typing import Any, Callable, Dict, NoReturn

from aiohttp import web


class WebSocketJsonBroadcaster:
    def __init__(
        self,
    ) -> None:
        self._clients = set()

    def add_client(self, websocket: web.WebSocketResponse) -> None:
        self._clients.add(websocket)

    def remove_client(self, websocket: web.WebSocketResponse) -> None:
        self._clients.discard(websocket)

    def remove_all_clients(self) -> None:
        self._clients.clear()

    async def _send_json(self, websocket: web.WebSocketResponse, message) -> None:
        try:
            await websocket.send_json(message)
        except ConnectionResetError:
            self.remove_client(websocket)

    async def broadcast_json(self, message: Dict[str, Any]) -> None:
        if self._clients:
            tasks = [self._send_json(websocket, message) for websocket in self._clients]
            await asyncio.gather(*tasks)


async def run_endless_broadcast(
    broadcaster: WebSocketJsonBroadcaster,
    source: Callable[..., Dict[str, Any]],
    delay: int | float = 1,
) -> NoReturn:
    while True:
        data = source()
        await broadcaster.broadcast_json(data)
        await asyncio.sleep(delay)
