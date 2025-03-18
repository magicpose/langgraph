#!/user/bin/env python3
# -*- coding: utf-8 -*-
# from smolagents import CodeAgent, OpenAIServerModel
# from smolagents.tools import Tool


code_str = ''

with open('langchain_tools_demo.py', 'r', encoding='utf-8') as f:
    code_str = f.read()

print(code_str)


Tool()
# tool = Tool().from_code(code_str)

model = OpenAIServerModel(
    model_id="DeepSeek-R1-Distill-Qwen-32B",
    api_base="http://ai-api.e-tudou.com:9000/v1/",  # Leave this blank to query OpenAI servers.
    api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57',  # Switch to the API key for the server you're targeting.
)

agent = CodeAgent(model=model, tools=[DownloadsTool()], add_base_tools=True)
# agent = CodeAgent(model=model, tools=[tool], add_base_tools=True)

print(agent.run("text-classification相应的模型信息都有哪些"))
