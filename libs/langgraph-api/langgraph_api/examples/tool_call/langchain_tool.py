#!/user/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import types

from anthropic import BaseModel
from langchain.agents import initialize_agent
from langchain.tools import BaseTool
from typing import Any, Optional
import asyncio
import os
import json

from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import Field

from langgraph_api.http_utils import start_skill_client, get_skill_client


code_str = '''
def tianYanCha(word: str):

    import os
    import json
    
    from langgraph_api.http_utils import get_skill_client
    
    from sdk import glo, SkillRequest
    from sdk.skillcore import RawDataParam
    
    # 设置全局基础主机
    glo.set_base_host("http://10.0.36.113:9080")
    
    # 定义请求头
    headers = {
        "satoken": "671735d7-5e31-47a2-956e-36ce13e36218",
        "bizToken": "123123"
    }
   
    # 创建参数对象
    r_param = RawDataParam(
        skill_id="1838024511136010240",
        header=headers,
        data={"word": word}
    )

    # 执行异步请求
    client = get_skill_client()
    result = client.get_raw_data(r_param)
    res = json.dumps(result, ensure_ascii=False)
    print(res)
    
    return res

'''

code_str1 = '''
async def tianYanCha(word: str):

    import os
    import json

    from langgraph_api.http_utils import get_skill_client

    from sdk import glo, SkillRequest
    from sdk.skillcore import RawDataParam

    # 设置全局基础主机
    glo.set_base_host("http://10.0.36.113:9080")

    # 定义请求头
    headers = {
        "satoken": "671735d7-5e31-47a2-956e-36ce13e36218",
        "bizToken": "123123"
    }

    # 创建参数对象
    r_param = RawDataParam(
        skill_id="1838024511136010240",
        header=headers,
        data={"word": word}
    )

    # 执行异步请求
    client = get_skill_client()
    result = await client.a_get_raw_data(r_param)
    res = json.dumps(result, ensure_ascii=False)
    print(res)

    return res

'''


async def main():
    # print(f"code:{code_str}")
    await start_skill_client()
    # client = get_skill_client()

    from langchain_core.tools import StructuredTool

    module = types.ModuleType("dynamic_tool")
    exec(code_str, module.__dict__)

    tool_func = next((obj for _, obj in inspect.getmembers(module, inspect.isfunction)), None)

    if tool_func is None:
        raise ValueError("No Tool function found in the code.")

    tool = StructuredTool.from_function(func=tool_func, description="""用于通过天眼查接口获取企业基本信息
    Args:
        word (str): 查询的企业名称
    Returns:
        天眼查企业信息
    """)
    # res = tool.run(**{"word": "土豆数据"})
    res = tool.invoke({"word": "土豆数据"})
    print(res)


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print("start")
    return a * b


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


calculator = StructuredTool.from_function(
    func=multiply,
    name="Calculator",
    description="multiply numbers",
    args_schema=CalculatorInput,
    return_direct=True
)

async def main1():
    # print(f"code:{code_str}")
    await start_skill_client()
    # client = get_skill_client()

    from langchain_core.tools import StructuredTool

    module = types.ModuleType("dynamic_tool")
    exec(code_str1, module.__dict__)

    tool_func = next((obj for _, obj in inspect.getmembers(module, inspect.isfunction)), None)

    if tool_func is None:
        raise ValueError("No Tool function found in the code.")

    tool = StructuredTool.from_function(coroutine=tool_func, description="""用于通过天眼查接口获取企业基本信息""")

    # res = await tool.ainvoke({"word": "土豆数据"})
    #
    # print(res)
    # model = ChatOpenAI(model="AgentOS-Chat-72B")
    model = ChatOpenAI(model="gpt-4o")


    # model.bind_tools([tool, calculator])
    result = agent.run("Use the Calculator tool to multiply 2 and 3.")
    print(result)
    # print(model.invoke("Use the Calculator tool to multiply 2 and 3."))


if __name__ == '__main__':

    asyncio.run(main1())
