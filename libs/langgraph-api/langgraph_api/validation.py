import pathlib

import jsonschema_rs
import orjson

from langgraph_api.api.openapi import get_openapi_spec

with open(pathlib.Path(__file__).parent / "openapi.json") as f:
    openapi_str = f.read()

openapi = orjson.loads(openapi_str)

AssistantVersionsSearchRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["AssistantVersionsSearchRequest"]
)
AssistantSearchRequest = jsonschema_rs.validator_for(
    # orjson.loads(get_openapi_spec())["components"]["schemas"]["AssistantSearchRequest"]
    openapi["components"]["schemas"]["AssistantSearchRequest"]
)
ShortcutSearchRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["ShortcutSearchRequest"]
)
ThreadSearchRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["ThreadSearchRequest"]
)
AssistantCreate = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["AssistantCreate"]
)
AssistantPatch = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["AssistantPatch"]
)
AssistantVersionChange = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["AssistantVersionChange"]
)
ThreadCreate = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["ThreadCreate"]
)
ThreadPatch = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["ThreadPatch"]
)
ThreadStateUpdate = jsonschema_rs.validator_for(
    {
        **openapi["components"]["schemas"]["ThreadStateUpdate"],
        "components": {
            "schemas": {
                "CheckpointConfig": openapi["components"]["schemas"]["CheckpointConfig"]
            }
        },
    }
)
ThreadStateCheckpointRequest = jsonschema_rs.validator_for(
    {
        **openapi["components"]["schemas"]["ThreadStateCheckpointRequest"],
        "components": {
            "schemas": {
                "CheckpointConfig": openapi["components"]["schemas"]["CheckpointConfig"]
            }
        },
    }
)
ThreadStateSearch = jsonschema_rs.validator_for(
    {
        **openapi["components"]["schemas"]["ThreadStateSearch"],
        "components": {
            "schemas": {
                "CheckpointConfig": openapi["components"]["schemas"]["CheckpointConfig"]
            }
        },
    }
)
RunCreateStateless = jsonschema_rs.validator_for(
    {
        **openapi["components"]["schemas"]["RunCreateStateless"],
        "components": {
            "schemas": {
                "Command": openapi["components"]["schemas"]["Command"],
                "Send": openapi["components"]["schemas"]["Send"],
            }
        },
    }
)
RunBatchCreate = jsonschema_rs.validator_for(
    {
        **openapi["components"]["schemas"]["RunBatchCreate"],
        "components": {
            "schemas": {
                "RunCreateStateless": openapi["components"]["schemas"][
                    "RunCreateStateless"
                ],
                "Command": openapi["components"]["schemas"]["Command"],
                "Send": openapi["components"]["schemas"]["Send"],
            }
        },
    }
)
RunCreateStateful = jsonschema_rs.validator_for(
    {
        **openapi["components"]["schemas"]["RunCreateStateful"],
        "components": {
            "schemas": {
                "CheckpointConfig": openapi["components"]["schemas"][
                    "CheckpointConfig"
                ],
                "Command": openapi["components"]["schemas"]["Command"],
                "Send": openapi["components"]["schemas"]["Send"],
            }
        },
    }
)
CronCreate = jsonschema_rs.validator_for(openapi["components"]["schemas"]["CronCreate"])
CronSearch = jsonschema_rs.validator_for(openapi["components"]["schemas"]["CronSearch"])


# Stuff around storage/BaseStore API
StorePutRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["StorePutRequest"]
)
StoreSearchRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["StoreSearchRequest"]
)
StoreDeleteRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["StoreDeleteRequest"]
)
StoreListNamespacesRequest = jsonschema_rs.validator_for(
    openapi["components"]["schemas"]["StoreListNamespacesRequest"]
)


DOCS_HTML = """<!doctype html>
<html>
  <head>
    <title>Scalar API Reference</title>
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <script id="langgraph_api-reference" data-url="/openapi.json"></script>
    <script>
      var configuration = {}
      document.getElementById('langgraph_api-reference').dataset.configuration =
        JSON.stringify(configuration)
    </script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>"""
