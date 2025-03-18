#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os

from sdk.skillcore import glo
import json
from sdk import SkillRequest
from smolagents import Tool


from langgraph_api.config import AGENT_AUTH_ENDPOINT
from langgraph_api.examples.tool_call.smolagent_tool import query_skill_detailTool
from langgraph_api.http_utils import start_skill_client
from langgraph_api.tools.skill2clazz import SkillGenerator

glo.set_base_host(AGENT_AUTH_ENDPOINT)

sdk = SkillRequest()


async def main():
    details = sdk.skill_details(skill_ids=['1838024511136010240'], tenant_id='1')
    details_map = {}
    detail = details[0]
    if hasattr(detail, 'data') and detail.data and 'id' in detail.data:
        details_map[detail.data['id']] = detail.data

    generated_code = SkillGenerator.generate(detail.data)

    print(generated_code)
    tool = Tool().from_code(generated_code)
    tool.forward({"word": "土豆数据", "langfuse_token": ""})


async def abc():
    code_str = ''

    with open('smolagent_tool.py', 'r', encoding='utf-8') as f:
        code_str = f.read()

    print(code_str)
    tool = Tool().from_code(code_str)
    # tool = query_skill_detailTool()
    print(tool.forward(id="1772501205906386944", langfuse_token="671735d7-5e31-47a2-956e-36ce13e36218"))


if __name__ == '__main__':
    pass
    # asyncio.run(main())
    asyncio.run(abc())

    # print(tianyanchaTool().forward('土豆数据'))
