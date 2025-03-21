import asyncio
import os
from datetime import UTC, datetime

import langgraph.version
import orjson
import structlog

from langgraph_api.config import LANGGRAPH_CLOUD_LICENSE_KEY, LANGSMITH_API_KEY
from langgraph_api.http_utils import http_request
from langgraph_license.validation import plus_features_enabled

logger = structlog.stdlib.get_logger(__name__)

INTERVAL = 300
REVISION = os.getenv("LANGSMITH_LANGGRAPH_API_REVISION")
VARIANT = os.getenv("LANGSMITH_LANGGRAPH_API_VARIANT")
if VARIANT == "cloud":
    HOST = "saas"
elif os.getenv("LANGSMITH_HOST_PROJECT_ID"):
    HOST = "byoc"
else:
    HOST = "self-hosted"
PLAN = "enterprise" if plus_features_enabled() else "developer"

LOGS: list[dict] = []
RUN_COUNTER = 0
NODE_COUNTER = 0
FROM_TIMESTAMP = datetime.now(UTC).isoformat()


def incr_runs(*, incr: int = 1) -> None:
    global RUN_COUNTER
    RUN_COUNTER += incr


def incr_nodes(_, *, incr: int = 1) -> None:
    global NODE_COUNTER
    NODE_COUNTER += incr


def append_log(log: dict) -> None:
    if not LANGGRAPH_CLOUD_LICENSE_KEY and not LANGSMITH_API_KEY:
        return

    global LOGS
    LOGS.append(log)


async def metadata_loop() -> None:
    # todo
    return

    if not LANGGRAPH_CLOUD_LICENSE_KEY and not LANGSMITH_API_KEY:
        return

    logger.info("Starting metadata loop")

    global RUN_COUNTER, NODE_COUNTER, FROM_TIMESTAMP
    while True:
        # because we always read and write from coroutines in main thread
        # we don't need a lock as long as there's no awaits in this block
        from_timestamp = FROM_TIMESTAMP
        to_timestamp = datetime.now(UTC).isoformat()
        nodes = NODE_COUNTER
        runs = RUN_COUNTER
        logs = LOGS.copy()
        LOGS.clear()
        RUN_COUNTER = 0
        NODE_COUNTER = 0
        FROM_TIMESTAMP = to_timestamp

        payload = {
            "license_key": LANGGRAPH_CLOUD_LICENSE_KEY,
            "api_key": LANGSMITH_API_KEY,
            "from_timestamp": from_timestamp,
            "to_timestamp": to_timestamp,
            "tags": {
                "langgraph.python.version": langgraph.version.__version__,
                "langgraph.platform.revision": REVISION,
                "langgraph.platform.variant": VARIANT,
                "langgraph.platform.host": HOST,
                "langgraph.platform.plan": PLAN,
            },
            "measures": {
                "langgraph.platform.runs": runs,
                "langgraph.platform.nodes": nodes,
            },
            "logs": logs,
        }
        try:
            # 在平台保存元数据信息
            await http_request(
                "POST",
                "https://api.smith.langchain.com/v1/metadata/submit",
                body=orjson.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            # retry on next iteration
            incr_runs(incr=runs)
            incr_nodes("", incr=nodes)
            FROM_TIMESTAMP = from_timestamp
            logger.warning("Failed to submit metadata", exc_info=e)
        await asyncio.sleep(INTERVAL)
