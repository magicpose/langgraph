import contextlib
import itertools
import json
import logging
import os
import pathlib
import threading
from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

from langgraph_api.config import LANGSMITH_SMITH_URL, LANGSERVE_PLUGINS, LANGSERVE_GRAPHS

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# import langfuse

from langfuse.callback import CallbackHandler

# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler(
    public_key=os.environ.get('LANGFUSE_PUBLIC_KEY'),
    secret_key=os.environ.get('LANGFUSE_SECRET_KEY'),
    host=os.environ.get('LANGFUSE_HOST')
)

PHOENIX_COLLECTOR_ENDPOINT = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
if PHOENIX_COLLECTOR_ENDPOINT:
    from phoenix.otel import register

    tracer_provider = register(
        project_name=os.environ.get('PHOENIX_PROJECT', 'default'),
        endpoint=os.environ.get("PHOENIX_COLLECTOR_ENDPOINT") + "/v1/traces",
        set_global_tracer_provider=True,
        auto_instrument=True
    )


def _get_org_id() -> str | None:
    from langsmith.client import Client
    from langsmith.utils import tracing_is_enabled

    # Yes, the organizationId is actually the workspace iD
    # which is actually the tenantID which we actually get via
    # the sessions endpoint
    if not tracing_is_enabled():
        return
    client = Client()
    try:
        response = client.request_with_retries(
            "GET", "/langgraph_api/v1/sessions", params={"limit": 1}
        )
        result = response.json()
        if result:
            return result[0]["tenant_id"]
    except Exception as e:
        logger.debug("Failed to get organization ID: %s", str(e))
        return None


@contextlib.contextmanager
def patch_environment(**kwargs):
    """Temporarily patch environment variables.

    Args:
        **kwargs: Key-value pairs of environment variables to set.

    Yields:
        None
    """
    original = {}
    try:
        for key, value in kwargs.items():
            if value is None:
                original[key] = os.environ.pop(key, None)
                continue
            original[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class IndexConfig(TypedDict, total=False):
    """Configuration for indexing documents for semantic search in the store."""

    dims: int
    """Number of dimensions in the embedding vectors.
    
    Common embedding models have the following dimensions:
        - OpenAI text-embedding-3-large: 256, 1024, or 3072
        - OpenAI text-embedding-3-small: 512 or 1536
        - OpenAI text-embedding-ada-002: 1536
        - Cohere embed-english-v3.0: 1024
        - Cohere embed-english-light-v3.0: 384
        - Cohere embed-multilingual-v3.0: 1024
        - Cohere embed-multilingual-light-v3.0: 384
    """

    embed: str
    """Either a path to an embedding model (./path/to/file.py:embedding_model)
    or a name of an embedding model (openai:text-embedding-3-small)
    
    Note: LangChain is required to use the model format specification.
    """

    fields: list[str] | None
    """Fields to extract text from for embedding generation.
    
    Defaults to the root ["$"], which embeds the json object as a whole.
    """


class StoreConfig(TypedDict, total=False):
    index: IndexConfig


class SecurityConfig(TypedDict, total=False):
    securitySchemes: dict
    security: list
    # path => {method => security}
    paths: dict[str, dict[str, list]]


class AuthConfig(TypedDict, total=False):
    path: str
    """Path to the authentication function in a Python file."""
    disable_studio_auth: bool
    """Whether to disable auth when connecting from the LangSmith Studio."""
    openapi: SecurityConfig
    """The schema to use for updating the openapi spec.

    Example:
        {
            "securitySchemes": {
                "OAuth2": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "tokenUrl": "/token",
                            "scopes": {
                                "me": "Read information about the current user",
                                "items": "Access to create and manage items"
                            }
                        }
                    }
                }
            },
            "security": [
                {"OAuth2": ["me"]}  # Default security requirement for all endpoints
            ]
        }
    """


def run_server(
    host: str = "127.0.0.1",
    port: int = 2024,
    reload: bool = False,
    graphs: dict | None = None,
    plugins: dict | None = None,
    n_jobs_per_worker: int | None = None,
    env_file: str | None = None,
    open_browser: bool = False,
    debug_port: int | None = None,
    wait_for_client: bool = False,
    env: str | pathlib.Path | Mapping[str, str] | None = None,
    reload_includes: Sequence[str] | None = None,
    reload_excludes: Sequence[str] | None = None,
    store: StoreConfig | None = None,
    auth: AuthConfig | None = None,
    **kwargs: Any,
):
    """Run the LangGraph API server."""
    import inspect

    import uvicorn

    env_vars = env if isinstance(env, Mapping) else None
    if isinstance(env, str | pathlib.Path):
        try:
            from dotenv.main import DotEnv

            env_vars = DotEnv(dotenv_path=env).dict() or {}
            logger.debug(f"Loaded environment variables from {env}: {sorted(env_vars)}")

        except ImportError:
            logger.warning(
                "python_dotenv is not installed. Environment variables will not be available."
            )

    if debug_port is not None:
        try:
            import debugpy
        except ImportError:
            logger.warning("debugpy is not installed. Debugging will not be available.")
            logger.info("To enable debugging, install debugpy: pip install debugpy")
            return
        debugpy.listen((host, debug_port))
        logger.info(
            f"🐛 Debugger listening on port {debug_port}. Waiting for client to attach..."
        )
        logger.info("To attach the debugger:")
        logger.info("1. Open your python debugger client (e.g., Visual Studio Code).")
        logger.info(
            "2. Use the 'Remote Attach' configuration with the following settings:"
        )
        logger.info("   - Host: 0.0.0.0")
        logger.info(f"   - Port: {debug_port}")
        logger.info("3. Start the debugger to connect to the server.")
        if wait_for_client:
            debugpy.wait_for_client()
            logger.info("Debugger attached. Starting server...")

    local_url = f"http://{host}:{port}"
    studio_url = LANGSMITH_SMITH_URL

    def _open_browser():
        nonlocal studio_url
        import time
        import urllib.request
        import webbrowser
        from concurrent.futures import ThreadPoolExecutor

        thread_logger = logging.getLogger("browser_opener")
        if not thread_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            thread_logger.addHandler(handler)

        with ThreadPoolExecutor(max_workers=1) as executor:
            org_id_future = executor.submit(_get_org_id)

            while True:
                try:
                    with urllib.request.urlopen(f"{local_url}/ok") as response:
                        if response.status == 200:
                            try:
                                org_id = org_id_future.result(timeout=3.0)
                                if org_id:
                                    studio_url = f"{os.environ.get('LANGSMITH_SMITH_URL')}?baseUrl={local_url}&organizationId={org_id}"
                            except TimeoutError as e:
                                thread_logger.debug(
                                    f"Failed to get organization ID: {str(e)}"
                                )

                            thread_logger.info("🎨 Opening Studio in your browser...")
                            thread_logger.info("URL: " + studio_url)
                            webbrowser.open(studio_url)
                            return
                except urllib.error.URLError:
                    pass
                time.sleep(0.1)

    welcome = f"""

        Welcome to

╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

- 🚀 API: \033[36m{local_url}\033[0m
- 🎨 Studio UI: \033[36m{studio_url}\033[0m
- 📚 API Docs: \033[36m{local_url}/docs\033[0m

This in-memory server is designed for development and testing.
For production use, please use LangGraph Cloud.

"""
    logger.info(welcome)
    with patch_environment(
        MIGRATIONS_PATH="__inmem",
        DATABASE_URL=":memory:",
        REDIS_URL="fake",
        N_JOBS_PER_WORKER=str(n_jobs_per_worker if n_jobs_per_worker else 1),
        LANGGRAPH_STORE=json.dumps(store) if store else None,
        LANGSERVE_GRAPHS=json.dumps(graphs) if graphs else None,
        # LANGSERVE_PLUGINS=json.dumps(plugins) if plugins else None,
        LANGSMITH_LANGGRAPH_API_VARIANT="local_dev",
        LANGGRAPH_AUTH=json.dumps(auth) if auth else None,
        **(env_vars or {}),
    ):
        if open_browser:
            threading.Thread(target=_open_browser, daemon=True).start()
        supported_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in inspect.signature(uvicorn.run).parameters
        }

        uvicorn.run(
            "langgraph_api.server:app",
            host=host,
            port=port,
            reload=reload,
            env_file=env_file,
            access_log=False,
            reload_includes=reload_includes,
            reload_excludes=reload_excludes,
            log_config={
                "version": 1,
                "incremental": False,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "class": "langgraph_api.logging_utils.Formatter",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "simple",
                        "stream": "ext://sys.stdout",
                    }
                },
                "root": {"handlers": ["console"]},
            },
            **supported_kwargs,
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CLI entrypoint for running the LangGraph API server."
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=2024, help="Port to bind the server to"
    )
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument(
        "--config", default="langgraph.json", help="Path to configuration file"
    )
    parser.add_argument(
        "--n-jobs-per-worker",
        type=int,
        help="Number of jobs per worker. Default is None (meaning 10)",
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Disable automatic browser opening"
    )
    parser.add_argument(
        "--debug-port", type=int, help="Port for debugger to listen on (default: none)"
    )
    parser.add_argument(
        "--wait-for-client",
        action="store_true",
        help="Whether to break and wait for a debugger to attach",
    )

    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config_data = json.load(f)

    mem_graphs = json.loads(LANGSERVE_GRAPHS) if LANGSERVE_GRAPHS else {}
    graphs = {**config_data.get("graphs", {}), **mem_graphs}
    mem_plugins = json.loads(LANGSERVE_PLUGINS) if LANGSERVE_PLUGINS else {}
    plugins = {**config_data.get("plugins", {}), **mem_plugins}
    auth = config_data.get("auth")
    run_server(
        args.host,
        args.port,
        not args.no_reload,
        graphs,
        plugins,
        n_jobs_per_worker=args.n_jobs_per_worker,
        open_browser=not args.no_browser,
        debug_port=args.debug_port,
        wait_for_client=args.wait_for_client,
        env=config_data.get("env", None),
        auth=auth,
    )


if __name__ == "__main__":
    main()
