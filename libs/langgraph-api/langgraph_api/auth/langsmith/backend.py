from typing import NotRequired, TypedDict

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.requests import HTTPConnection

from langgraph_api.auth.langsmith.client import auth_client
from langgraph_api.auth.studio_user import StudioUser
from langgraph_api.config import (
    LANGSMITH_AUTH_VERIFY_TENANT_ID,
    LANGSMITH_TENANT_ID, AGENT_AUTH_ENDPOINT,
)


class AuthDict(TypedDict):
    organization_id: str
    tenant_id: str
    user_id: NotRequired[str]
    user_email: NotRequired[str]


class LangsmithAuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, BaseUser] | None:
        headers = [
            ("Authorization", conn.headers.get("Authorization")),
            ("Sa-token", conn.headers.get("satoken")),
            ("X-Tenant-Id", conn.headers.get("x-tenant-id")),
            ("X-Api-Key", conn.headers.get("x-langgraph_api-key")),
            # ("X-Service-Key", conn.headers.get("x-service-key")),
        ]
        if not any(h[1] for h in headers):
            raise AuthenticationError("Missing authentication headers")
        async with auth_client() as auth:
            # 这里调用接口获取用户信息
            token = conn.headers.get("Authorization") or conn.headers.get("satoken")
            x_api_key = conn.headers.get("x-langgraph_api-key")

            auth_dict = dict()

            if token:
                res = await auth.get(
                    f"/sa/v1/langgraph_api/management/user/getUserByToken?token={token}",
                    headers=[h for h in headers if h[1] is not None]
                )
                if res.status_code == 401:
                    raise AuthenticationError("Invalid token")
                elif res.status_code == 403:
                    raise AuthenticationError("Forbidden")
                elif 210 > res.status_code >= 200:
                    r = res.json()
                    if not r or r.get("code") != 1 or not r.get("data"):
                        raise AuthenticationError("Invalid token")

                    data = r.get("data")
                    auth_dict = {
                        "organization_id": data.get('orgListStr'),
                        "tenant_id": data.get("tenantId"),
                        "user_id": data.get("id"),
                        "user_email": data.get("email"),
                        "token": token
                    }

            elif x_api_key:
                res = await auth.get(
                    f"/aosc/v1/openapi/agent/getByAgentKey/{x_api_key}"
                )
                if res.status_code == 401:
                    raise AuthenticationError("Invalid token")
                elif res.status_code == 403:
                    raise AuthenticationError("Forbidden")
                elif 210 > res.status_code >= 200:
                    r = res.json()
                    if not r or r.get("code") != 1 or not r.get("data"):
                        raise AuthenticationError("Invalid token")

                    token = r.get("data").get("token")

                    if not token:
                        raise AuthenticationError("Invalid token")

                    res = await auth.get(
                        f"/sa/v1/langgraph_api/management/user/getUserByToken?token={token}",
                        headers=[h for h in headers if h[1] is not None]
                    )
                    if res.status_code == 401:
                        raise AuthenticationError("Invalid token")
                    elif res.status_code == 403:
                        raise AuthenticationError("Forbidden")
                    elif 210 > res.status_code >= 200:
                        r = res.json()
                        if not r or r.get("code") != 1 or not r.get("data"):
                            raise AuthenticationError("Invalid token")

                        data = r.get("data")
                        auth_dict = {
                            "organization_id": data.get('orgListStr'),
                            "tenant_id": data.get("tenantId"),
                            "user_id": data.get("id"),
                            "user_email": data.get("email"),
                            "token": token
                        }

            else:
                raise AuthenticationError("Forbidden")

            # If tenant id verification is disabled, the bearer token requests
            # are not required to match the tenant id. Api key requests are
            # always required to match the tenant id.
            if LANGSMITH_AUTH_VERIFY_TENANT_ID or conn.headers.get("x-langgraph_api-key"):
                if auth_dict.get("tenant_id") != LANGSMITH_TENANT_ID:
                    raise AuthenticationError("Invalid tenant ID")

            studio_user = StudioUser(
                auth_dict.get("user_id"), is_authenticated=True
            )

            studio_user.token = token

        return AuthCredentials(["authenticated"]), studio_user
