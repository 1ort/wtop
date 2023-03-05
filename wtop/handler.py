from typing import Any, Callable, Coroutine, Dict, Protocol

import aiohttp
from aiohttp import web


class Subscription(Protocol):
    def add_client(self, websocket: web.WebSocketResponse) -> None:
        pass

    def remove_client(self, websocket: web.WebSocketResponse) -> None:
        pass


def json_stats_handler(
    source: Callable[..., Dict[str, Any]],
) -> Callable[[web.Request], Coroutine[Any, Any, web.Response]]:
    async def handler(request: web.Request) -> web.Response:
        return web.json_response(source())

    return handler


def websocket_stats_handler(
    subscription: Subscription,
) -> Callable[[web.Request], Coroutine[Any, Any, web.WebSocketResponse]]:
    async def handler(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        subscription.add_client(ws)
        try:
            await listen_websocket(ws)
        finally:
            await ws.close()
            subscription.remove_client(ws)
        return ws

    return handler


async def listen_websocket(ws: web.WebSocketResponse) -> None:
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT and msg.data == "close":
            break
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break


async def root_handler(request: web.Request) -> web.HTTPFound:
    return web.HTTPFound("/stats.html")
