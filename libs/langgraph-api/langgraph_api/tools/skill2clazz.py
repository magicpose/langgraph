import os
from typing import Dict, Any
import json


class SkillGenerator:
    # 输入参数格式模板
    INPUT_TEMPLATE = {
        "type": "string",
        "require": False,
        "description": "",
        "param_type": ""
    }

    TEMPLATE = '''# -*- coding: utf-8 -*-
"""
技能ID: {skill_id}
技能名称: {name}
"""

import asyncio
import json
import os
from smolagents import Tool
from typing import Optional

from sdk.skillcore import RawDataParam


class {en_name}Tool(Tool):
    """
    {description}
    """
    name = "{name}"
    description = """{description}"""
    inputs = {inputs}
    output_type = 'string'

    def forward({params}) -> str:
        from langgraph_api.http_utils import get_skill_client

        client = get_skill_client()
        data = {{}}
        
        # Initialize parameter containers
{param_handling}

        headers = {{
            "satoken": langfuse_token,
            "bizToken": "{skill_biz_token}"
        }}
        
        # Create parameter object
        r_param = RawDataParam(
            skill_id="{skill_id}", 
            header=headers,
            data=data)

        # Execute request
        result = client.get_raw_data(r_param)
        return json.dumps(result, ensure_ascii=False)

'''

    @classmethod
    def _build_params_def(cls, inputs: Dict) -> str:
        """构建函数参数定义"""
        params = ['self']
        for name, config in inputs.items():
            param_type = ': Optional[str] = None' if not config['require'] else ': str'
            params.append(f'{name}{param_type}')
        return ', '.join(params)

    @classmethod
    def _build_param_handling(cls, detail: Dict) -> str:
        """构建参数处理代码块"""
        param_blocks = []

        # 处理请求参数
        if 'requestParam' in detail and detail['requestParam'].get('properties'):
            params = list(detail['requestParam']['properties'].keys())
            param_lines = []
            for param in params:
                param_lines.append(f'        if {param} is not None:')
                param_lines.append(f'            data["{param}"] = {param}')
            param_blocks.append('\n'.join(param_lines))

        # 处理路径变量
        if 'pathVariable' in detail and detail['pathVariable'].get('properties'):
            params = list(detail['pathVariable']['properties'].keys())
            param_lines = []
            for param in params:
                param_lines.append(f'        if {param} is not None:')
                param_lines.append(f'            data["{param}"] = {param}')
            param_blocks.append('\n'.join(param_lines))

        # 处理请求体
        if 'requestBody' in detail and detail['requestBody'].get('properties'):
            params = list(detail['requestBody']['properties'].keys())
            param_lines = []
            for param in params:
                param_lines.append(f'        if {param} is not None:')
                param_lines.append(f'            data["{param}"] = {param}')
            param_blocks.append('\n'.join(param_lines))

        # 处理表单数据
        if 'formData' in detail and detail['formData'].get('properties'):
            params = list(detail['formData']['properties'].keys())
            param_lines = []
            for param in params:
                param_lines.append(f'''        if {param} is not None:
            if isinstance({param}, str) and re.match(r'data:.*?;base64,.*?', {param}):
                file_name = f'{param}_default_name'
                file_byte = base64.b64decode({param}.split('base64,')[1])
                temp_file = io.BytesIO(file_byte)
                temp_file.name = file_name
                temp_file.seek(0)
                file_content_type = mimetypes.guess_type(file_name)[0]
                files_params["{param}"] = (file_name, temp_file, file_content_type)
            else:
                data_params["{param}"] = {param}''')
            param_blocks.append('\n'.join(param_lines))

        return '\n\n'.join(param_blocks) or '        pass  # No parameters to handle'

    @classmethod
    def _collect_inputs(cls, detail: Dict) -> Dict:
        """收集所有输入参数"""
        inputs = {}

        # 收集请求参数
        if 'requestParam' in detail and detail['requestParam'].get('properties'):
            for k, v in detail['requestParam']['properties'].items():
                input_config = cls.INPUT_TEMPLATE.copy()
                input_config.update({
                    "type": v.get('type', 'string'),
                    "require": v.get('required', False),
                    "description": v.get('description', ''),
                    "param_type": "query",
                })
                if not v.get('required', False):
                    input_config["nullable"] = True
                inputs[k] = input_config

        # 收集路径变量
        if 'pathVariable' in detail and detail['pathVariable'].get('properties'):
            for k, v in detail['pathVariable']['properties'].items():
                input_config = cls.INPUT_TEMPLATE.copy()
                input_config.update({
                    "type": v.get('type', 'string'),
                    "require": v.get('required', False),
                    "description": v.get('description', ''),
                    "param_type": "path"
                })
                if not v.get('required', False):
                    input_config["nullable"] = True
                inputs[k] = input_config

        # 收集请求体参数
        if 'requestBody' in detail and detail['requestBody'].get('properties'):
            for k, v in detail['requestBody']['properties'].items():
                input_config = cls.INPUT_TEMPLATE.copy()
                input_config.update({
                    "type": v.get('type', 'string'),
                    "require": v.get('required', False),
                    "description": v.get('description', ''),
                    "param_type": "body"
                })
                if not v.get('required', False):
                    input_config["nullable"] = True
                inputs[k] = input_config

        # 收集表单数据
        if 'formData' in detail and detail['formData'].get('properties'):
            for k, v in detail['formData']['properties'].items():
                input_config = cls.INPUT_TEMPLATE.copy()
                input_config.update({
                    "type": v.get('type', 'string'),
                    "require": v.get('required', False),
                    "description": v.get('description', ''),
                    "param_type": "form"
                })
                if not v.get('required', False):
                    input_config["nullable"] = True
                inputs[k] = input_config

        return inputs

    @classmethod
    def _format_json(cls, obj: Dict) -> str:
        """格式化JSON字符串，确保最后的大括号缩进正确"""
        # 先用json.dumps生成格式化的字符串
        json_str = json.dumps(obj, indent=8, ensure_ascii=False)
        # 替换布尔值为Python格式
        json_str = json_str.replace('"require": false', '"require": False')
        json_str = json_str.replace('"require": true', '"require": True')

        json_str = json_str.replace('"nullable": false', '"nullable": False')
        json_str = json_str.replace('"nullable": true', '"nullable": True')
        # 分割成行
        lines = json_str.split('\n')
        # 处理最后一个大括号的缩进
        if lines and lines[-1].strip() == '}':
            lines[-1] = '    }'
        # 重新组合
        return '\n'.join(lines)

    @classmethod
    def generate(cls, detail: Dict[str, Any]) -> str:
        """生成完整的技能代码"""
        # 收集所有输入参数
        inputs = cls._collect_inputs(detail)

        # "langfuse_token: Optional[str] = None")
        inputs.setdefault("langfuse_token", {
            "type": "string",
            "require": False,
            "description": "user token",
            "param_type": "header",
            "nullable": True
        })

        # 格式化 inputs 字典和参数定义
        inputs_str = cls._format_json(inputs)
        params_def = cls._build_params_def(inputs)

        return cls.TEMPLATE.format(
            skill_id=detail['id'],
            en_name=detail.get('englishName'),
            name=detail['name'],
            description=detail.get('description', ''),
            skill_sdk_host=os.environ.get("AGENT_AUTH_ENDPOINT"),
            skill_biz_token="123123",
            inputs=inputs_str,
            params=params_def,
            param_handling=cls._build_param_handling(detail)
        )


if __name__ == "__main__":
    test_detail = {
        "id": "1886963254220570624",
        "name": "ProjectList",
        "description": "Get project list from PingCode",
        "requestParam": {
            "properties": {
                "identifier": {
                    "type": "string",
                    "required": True,
                    "description": "Identifier"
                },
                "type": {
                    "type": "string",
                    "required": True,
                    "description": "Type: waterfall/user"
                }
            }
        },
        "pathVariable": {
            "properties": {
                "projectId": {
                    "type": "string",
                    "required": False,
                    "description": "项目ID"
                }
            }
        },
        "requestBody": {
            "properties": {
                "name": {
                    "type": "string",
                    "required": False,
                    "description": "项目名称"
                }
            }
        }
    }
    generated_code = SkillGenerator.generate(test_detail)
    print(generated_code)
