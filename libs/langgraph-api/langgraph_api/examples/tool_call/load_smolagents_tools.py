#!/user/bin/env python3
# -*- coding: utf-8 -*-
from smolagents import CodeAgent, OpenAIServerModel, ToolCallingAgent
from smolagents.tools import Tool
from langgraph_api.examples.tool_call.smolagents_tools_demo import PingCodeListTool

code_str = ''

with open('smolagents_tools_demo.py', 'r', encoding='utf-8') as f:
    code_str = f.read()

print(code_str)
tool = Tool().from_code(code_str)

PingCodeListTool().forward('JFXM', 'waterfall')

model = OpenAIServerModel(
    model_id="DeepSeek-R1-Distill-Qwen-32B",
    api_base="http://ai-api.e-tudou.com:9000/v1/",  # Leave this blank to query OpenAI servers.
    api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57',  # Switch to the API key for the server you're targeting.
)

# code_agent = CodeAgent(model=model, tools=[PingCodeListTool()], add_base_tools=True)
code_agent = CodeAgent(model=model, tools=[tool], add_base_tools=True)
print(code_agent.run("帮我查询标识JFXM，类型是waterfall的pingcode项目列表信息"))
# tool_calling_agent = ToolCallingAgent(model=model, tools=[tool], add_base_tools=True)
# print(tool_calling_agent.run("帮我查询标识JFXM，类型是waterfall的pingcode项目列表信息"))
