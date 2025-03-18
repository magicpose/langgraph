# -*- coding: utf-8 -*-
"""
技能ID: 1886963254220570624
技能名称: ProjectList
"""

import base64
import io
import json
import mimetypes
import re
import requests
from sdk.skillcore import SkillExecutor, SkillAtom, SkillCenter
from smolagents import Tool
from sdk import SkillExecutorParam, glo
from typing import Optional

glo.set_base_host("http://10.0.36.113:9080")

headers = {
    "satoken": "475c223b-ed4f-492a-a28e-640f805e469a",
    "bizToken": "xaaaasadadasdadadadad"
}


class ProjectListTool(Tool):
    """
    Get project list from PingCode
    """
    name = "ProjectList"
    description = """Get project list from PingCode"""
    inputs = {
        "identifier": {
            "type": "string",
            "require": True,
            "description": "Identifier",
            "param_type": "query"
        },
        "type": {
            "type": "string",
            "require": True,
            "description": "Type: waterfall/user",
            "param_type": "query"
        },
        "projectId": {
            "type": "string",
            "require": False,
            "description": "项目ID",
            "param_type": "path",
            "nullable": True
        },
        "name": {
            "type": "string",
            "require": False,
            "description": "项目名称",
            "param_type": "body",
            "nullable": True
        }
    }
    output_type = 'string'

    def forward(self, identifier: str, type: str, projectId: Optional[str] = None, name: Optional[str] = None) -> str:
        # Initialize parameter containers
        path_params = {}
        query_params = {}
        body_params = {}
        data_params = {}
        files_params = {}

        if identifier is not None:
            query_params["identifier"] = identifier
        if type is not None:
            query_params["type"] = type

        if projectId is not None:
            path_params["projectId"] = projectId

        if name is not None:
            body_params["name"] = name

        # Create parameter object
        param = SkillExecutorParam(
            skill_id="1886963254220570624",
            header=headers,
            path=path_params,
            params=query_params,
            body=body_params,
            form_data=data_params,
            files=files_params
        )

        # Execute request
        res = requests.post(
            'http://10.0.36.113:9080/asst/v1/api/get/raw_data',
            data=json.dumps(param.to_json())
        )

        return res.text
