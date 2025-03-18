import logging

import jsonschema_rs
from starlette.responses import Response
from starlette.routing import BaseRoute
from starlette.exceptions import HTTPException

from langgraph_api.route import ApiRequest, ApiResponse, ApiRoute
from langgraph_storage.database import connect
from langgraph_storage.ops import Plugins

from langgraph_api.validation import ShortcutSearchRequest
from langgraph_storage.retry import retry_db

logger = logging.getLogger(__name__)


@retry_db
async def search_shortcut_items(
    request: ApiRequest,
) -> ApiResponse:
    """List commands."""
    payload = await request.json(ShortcutSearchRequest)

    async with connect() as conn:
        plugins_iter = await Plugins.search(
            conn,
            type=payload.get("type"),
            metadata=payload.get("metadata"),
            limit=payload.get("limit") or 10,
            offset=payload.get("offset") or 0,
        )

    return ApiResponse([plugin async for plugin in plugins_iter])


shortcut_routes: list[BaseRoute] = [
    ApiRoute("/shortcuts/search", search_shortcut_items, methods=["POST"]),
]

shortcut_routes = [route for route in shortcut_routes if route is not None]
