import base64
import io
import json
import mimetypes
import re

import requests
from sdk.skillcore import SkillExecutor, SkillAtom, SkillCenter
from smolagents import Tool


from sdk import SkillExecutorParam, glo

glo.set_assistant_base_host("http://10.0.36.113:9080/asst")


class PingCodeListTool(Tool):
    name = "获取项目列表"
    description = """这个技能返回pingcode的项目信息"""
    inputs = {
        "identifier": {
            "type": "string",
            "require": False,
            "description": "标识符",
        },
        "type": {
            "type": "string",
            "require": False,
            "description": "类型：waterfall/user",
        }
    }
    output_type = 'string'

    def forward(self, identifier: str, type: str):
        headers = {
            "satoken": "475c223b-ed4f-492a-a28e-640f805e469a",
            "bizToken": "xaaaasadadasdadadadad"  # 生成方法见下
        }

        def convert_param(skill_details, data) -> (dict, dict, dict, dict, dict):
            """
            技能详情参数转化
                param: 参数
                    skill_id: 技能ID
                    data: 模型返回填充的参数结构
                result: 返回结果
                    path_params: 路径中的参数
                    params: url后面的参数
                    body_params: post请求中的request_body参数
            """
            path_params, params, body_params, data_params, files_params = {}, {}, {}, {}, {}
            if not data:
                return path_params, params, body_params, data_params, files_params

            if not skill_details or skill_details['code'] != 1 or not skill_details['data']:
                raise "获取技能详情失败"
            skill_details_data = skill_details['data']

            request_param_tag = False
            if 'requestParam' in skill_details_data and skill_details_data['requestParam']:
                request_param_tag = True
                for k, v in skill_details_data['requestParam']['properties'].items():
                    if k in data:
                        params[k] = data[k]
            if 'pathVariable' in skill_details_data and skill_details_data['pathVariable']:
                request_param_tag = True
                for k, v in skill_details_data['pathVariable']['properties'].items():
                    if k in data:
                        path_params[k] = data[k]

            if 'requestBody' in skill_details_data and skill_details_data['requestBody']:
                if request_param_tag:
                    body_params = data['requestBody']
                else:
                    body_params = data

            if 'formData' in skill_details_data and skill_details_data['formData']:
                # 表单提交 amis 反显
                # 先看参数里面有没有文件的base64
                for k in list(data.keys()):
                    if re.match(r'data:.*?;base64,.*?', data[k]):
                        # 如果参数中含有文件的base64,把参数转成文件
                        file_name = data[f'{k}_default_name']
                        file_byte = base64.b64decode(data[k].split('base64,')[1])
                        temp_file = io.BytesIO(file_byte)
                        temp_file.name = file_name
                        temp_file.seek(0)
                        file_content_type = mimetypes.guess_type(file_name)[0]
                        files_params = {k: (file_name, temp_file, file_content_type)}
                        # 最后删除从data中这个k,v
                        data.pop(k)

                # data中的参数放入data_params
                for k, v in skill_details_data['formData']['properties'].items():
                    if k in data:
                        data_params[k] = data[k]

            return path_params, params, body_params, data_params, files_params

        data = {
            "identifier": identifier,
            "type": type
        }

        skill_details = SkillCenter.details('1886963254220570624').__dict__
        # todo 这里的参数转换会下沉到技能中心
        path_params, query_params, body_params, data_params, files_params = convert_param(skill_details, data)
        param = SkillExecutorParam(skill_id="1886963254220570624", header=headers, path=path_params, params=query_params, body=body_params)

        # todo 调用技能中心同步方法， 暂时调用技能中心api
        res = requests.post('http://10.0.36.113:9080/asst/v1/api/get/raw_data', data=json.dumps(param.to_json()))

        return res.text
