import asyncio

import aiohttp
from aiohttp import web
from broadcast import WebSocketStatsBroadcaster
from stats import StatCollector


def json_stats_handler(collector: StatCollector):
    async def handler(request: web.Request) -> web.Response:
        return web.json_response(collector.get_stats())

    return handler


def websocket_stats_handler(broadcaster: WebSocketStatsBroadcaster):
    async def handler(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        broadcaster.add_client(ws)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT and msg.data == "close":
                    await ws.close()
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        finally:
            broadcaster.remove_client(ws)
        return ws

    return handler


async def root_handler(request) -> web.HTTPFound:
    return web.HTTPFound("/stats.html")


def run():
    app = web.Application()
    collector = StatCollector()
    broadcaster = WebSocketStatsBroadcaster(collector)
    app.add_routes(
        [
            web.get("/stats.json", json_stats_handler(collector)),
            web.get("/stats.ws", websocket_stats_handler(broadcaster)),
            web.get("/", root_handler),
        ]
    )
    app.router.add_static("/", "./wtop/static/", show_index=False)

    async def _on_startup(app):
        collector.run_in_thread()
        asyncio.create_task(broadcaster.run(delay=1))

    async def _on_cleanup(app):
        broadcaster.remove_all_clients()

    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_on_cleanup)
    web.run_app(app)


if __name__ == "__main__":
    run()
