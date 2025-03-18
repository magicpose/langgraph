# -*- coding: utf-8 -*-
"""
技能ID: 1772501205906386944
技能名称: query_skill_detail
"""

import asyncio
import json
import os
from smolagents import Tool
from typing import Optional

from sdk.skillcore import RawDataParam

from langgraph_api.http_utils import get_skill_client


class query_skill_detailTool(Tool):
    """
    用于查询技能详情
    """
    name = "query_skill_detail"
    description = """用于查询技能详情"""
    inputs = {
        "id": {
            "type": "string",
            "require": False,
            "description": "要查询的技能id",
            "param_type": "path",
            "nullable": True
        },
        "langfuse_token": {
            "type": "string",
            "require": False,
            "description": "user token",
            "param_type": "header",
            "nullable": True
        }
    }
    output_type = 'string'

    def forward(self, id: Optional[str] = None, langfuse_token: Optional[str] = None) -> str:

        data = {}

        client = get_skill_client()

        # Initialize parameter containers
        if id is not None:
            data["id"] = id

        headers = {
            "satoken": langfuse_token,
            "bizToken": "123123"
        }

        # Create parameter object
        r_param = RawDataParam(
            skill_id="1772501205906386944",
            header=headers,
            data=data)

        # Execute request
        result = client.get_raw_data(r_param)
        return json.dumps(result, ensure_ascii=False)
