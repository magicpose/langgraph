from os import environ, getenv

import orjson
from starlette.config import Config, undefined
from starlette.datastructures import CommaSeparatedStrings

env = Config()


STATS_INTERVAL_SECS = env("STATS_INTERVAL_SECS", cast=int, default=60)
HTTP_CONCURRENCY = env("HTTP_CONCURRENCY", cast=int, default=10)

# storage

POSTGRES_URL = env("POSTGRES_URL", cast=str, default=":memory:")
MIGRATIONS_PATH = env("MIGRATIONS_PATH", cast=str, default="/storage/migrations")

# redis

REDIS_URL = env("REDIS_URL", cast=str, default=":memory:")
REDIS_MAX_CONNECTIONS = env("REDIS_MAX_CONNECTIONS", cast=int, default=500)

# server

CORS_ALLOW_ORIGINS = env("CORS_ALLOW_ORIGINS", cast=CommaSeparatedStrings, default="*")

# queue

BG_JOB_NO_DELAY = env("BG_JOB_NO_DELAY", cast=bool, default=False)
N_JOBS_PER_WORKER = env("N_JOBS_PER_WORKER", cast=int, default=10)
BG_JOB_TIMEOUT_SECS = env("BG_JOB_TIMEOUT_SECS", cast=float, default=3600)
FF_CRONS_ENABLED = env("FF_CRONS_ENABLED", cast=bool, default=True)
FF_JS_ZEROMQ_ENABLED = env("FF_JS_ZEROMQ_ENABLED", cast=bool, default=False)

# auth

# LANGGRAPH_AUTH_TYPE = env("LANGGRAPH_AUTH_TYPE", cast=str, default="noop")
LANGGRAPH_AUTH_TYPE = env("LANGGRAPH_AUTH_TYPE", cast=str, default="langsmith")


def _parse_auth(auth: str | None) -> dict | None:
    if not auth:
        return None
    parsed = orjson.loads(auth)
    if not parsed:
        return None
    return parsed


LANGGRAPH_AUTH = env("LANGGRAPH_AUTH", cast=_parse_auth, default=None)
LANGSMITH_TENANT_ID = env("LANGSMITH_TENANT_ID", cast=str, default="1")

AGENT_AUTH_ENDPOINT = env("AGENT_AUTH_ENDPOINT", cast=str, default="http://10.0.36.113:9080")
LANGSMITH_AUTH_VERIFY_TENANT_ID = env(
    "LANGSMITH_AUTH_VERIFY_TENANT_ID", cast=bool, default=True
)
LANGSMITH_SMITH_URL = env("LANGSMITH_SMITH_URL", cast=str, default="http://10.1.3.122:3005/project/cm6t5vtfw0006oh4ytrifbacf/traces")

# license

LANGGRAPH_CLOUD_LICENSE_KEY = env("LANGGRAPH_CLOUD_LICENSE_KEY", cast=str, default="")
LANGSMITH_API_KEY = env(
    "LANGSMITH_API_KEY", cast=str, default=getenv("LANGCHAIN_API_KEY", "")
)

# plugins

LANGSERVE_PLUGINS = env("LANGSERVE_PLUGINS", cast=str, default=getenv("LANGSERVE_PLUGINS", None))

# graphs

LANGSERVE_GRAPHS = env("LANGSERVE_GRAPHS", cast=str, default=getenv("LANGSERVE_GRAPHS", None))
