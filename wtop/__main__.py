import asyncio
from typing import Any, Callable, Coroutine

import handler as h
from aiohttp import web
from broadcast import WebSocketJsonBroadcaster, run_endless_broadcast
from stats import StatCollector


def on_startup(
    app: web.Application,
    collector: StatCollector,
    broadcaster: WebSocketJsonBroadcaster,
) -> Callable[..., Coroutine[Any, Any, None]]:
    async def inner(app: web.Application) -> None:
        app.add_routes(
            [
                web.get("/stats.json", h.json_stats_handler(collector.get_stats)),
                web.get("/stats.ws", h.websocket_stats_handler(broadcaster)),
                web.get("/", h.root_handler),
            ]
        )
        app.router.add_static("/", "./wtop/static/", show_index=False)

        collector.run_in_thread()
        asyncio.create_task(run_endless_broadcast(broadcaster, collector.get_stats))

    return inner


def on_cleanup(
    app: web.Application, broadcaster: WebSocketJsonBroadcaster
) -> Callable[..., Coroutine[Any, Any, None]]:
    async def inner(app: web.Application) -> None:
        broadcaster.remove_all_clients()

    return inner


app = web.Application()
collector = StatCollector()
broadcaster = WebSocketJsonBroadcaster()
app.on_startup.append(on_startup(app, collector, broadcaster))
app.on_cleanup.append(on_cleanup(app, broadcaster))
web.run_app(app)
