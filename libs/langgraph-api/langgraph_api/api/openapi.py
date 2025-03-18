import logging
from functools import lru_cache

import orjson

from langgraph_api.config import LANGGRAPH_AUTH, LANGGRAPH_AUTH_TYPE
from langgraph_api.graph import GRAPHS

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_openapi_spec() -> str:
    from langgraph_api.validation import openapi
    # patch the graph_id enums
    graph_ids = list(GRAPHS.keys())
    for schema in (
        "Assistant",
        "AssistantCreate",
        "AssistantPatch",
        "GraphSchema",
        "AssistantSearchRequest",
    ):
        openapi["components"]["schemas"][schema]["properties"]["graph_id"]["enum"] = (
            graph_ids
        )
    # patch the auth schemes
    if LANGGRAPH_AUTH_TYPE == "langsmith":
        openapi["security"] = [
            {"x-langgraph_api-key": []},
        ]
        openapi["components"]["securitySchemes"] = {
            "x-langgraph_api-key": {"type": "apiKey", "in": "header", "name": "x-langgraph_api-key"}
        }
    if LANGGRAPH_AUTH:
        # Allow user to specify OpenAPI security configuration
        if isinstance(LANGGRAPH_AUTH, dict) and "openapi" in LANGGRAPH_AUTH:
            openapi_config = LANGGRAPH_AUTH["openapi"]
            if isinstance(openapi_config, dict):
                # Add security schemes
                if "securitySchemes" in openapi_config:
                    openapi["components"]["securitySchemes"] = openapi_config[
                        "securitySchemes"
                    ]
                elif "security_schemes" in openapi_config:
                    # For our sorry python users
                    openapi["components"]["securitySchemes"] = openapi_config[
                        "security_schemes"
                    ]

                # Add default security if specified
                if "security" in openapi_config:
                    openapi["security"] = openapi_config["security"]

                if "paths" in openapi_config:
                    for path, methods in openapi_config["paths"].items():
                        if path in openapi["paths"]:
                            openapi_path = openapi["paths"][path]
                            for method, security in methods.items():
                                method = method.lower()
                                if method in openapi_path:
                                    openapi_path[method]["security"] = security
        else:
            logger.warning(
                "Custom authentication is enabled but no OpenAPI security configuration was provided. "
                "API documentation will not show authentication requirements. "
                "Add 'openapi' section to auth section of your `langgraph.json` file to specify security schemes."
            )
    return orjson.dumps(openapi)
