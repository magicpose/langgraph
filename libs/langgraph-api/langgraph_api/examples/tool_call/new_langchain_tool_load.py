#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os

from sdk.skillcore import glo
import json
from sdk import SkillRequest
from smolagents import Tool


from langgraph_api.config import AGENT_AUTH_ENDPOINT
from langgraph_api.tools.skill2clazz import SkillGenerator

glo.set_base_host(AGENT_AUTH_ENDPOINT)

sdk = SkillRequest()


async def main():
    details = await sdk.skill_details(skill_ids=['1838024511136010240'], tenant_id='1')
    details_map = {}
    detail = details[0]
    if hasattr(detail, 'data') and detail.data and 'id' in detail.data:
        details_map[detail.data['id']] = detail.data

    generated_code = SkillGenerator.generate(detail.data)

    print(generated_code)
    tool = Tool().from_code(generated_code)
    tool.forward("土豆数据")


async def act():
    tool = TianYanChaTool()
    return await tool.arun({"word": "你好"})


if __name__ == '__main__':
    # asyncio.run(main())
    # os.environ.setdefault("AGENT_AUTH_ENDPOINT", "http://10.0.36.113:9080")
    print(asyncio.run(act()))
