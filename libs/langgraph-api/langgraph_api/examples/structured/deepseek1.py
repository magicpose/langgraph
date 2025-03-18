#!/user/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint

from openai import OpenAI

from langchain_openai import ChatOpenAI
from smolagents import CodeAgent, OpenAIServerModel

from langgraph_api.examples.tool_call.smolagents_tools_demo import PingCodeListTool

# langchain
model = ChatOpenAI(model="DeepSeek-R1-Distill-Qwen-32B")

res = model.stream('怎么学好英文')
for r in res:
    print(r)

# smolagent
# model = OpenAIServerModel(
#     model_id="DeepSeek-R1-Distill-Qwen-32B",
#     api_base="http://ai-api.e-tudou.com:9000/v1/",  # Leave this blank to query OpenAI servers.
#     api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57',  # Switch to the API key for the server you're targeting.
# )



# agent = CodeAgent(model=model, tools=[PingCodeListTool()])
# agent.run('怎么学好英语')

# # 初始化客户端
# client = OpenAI()
#
# # 调用API生成对话
# completion = client.chat.completions.create(
#     model="DeepSeek-R1-Distill-Qwen-32B",  # 使用的模型
#     messages=[
#         {"role": "system", "content": "你是一个专业的助手，回答问题时必须准确，且不能胡言乱语。"},  # 系统提示
#         {"role": "user", "content": "怎么学好英文"}  # 用户输入
#     ],
#     temperature=0.7,  # 控制输出的随机性，值越低输出越确定
#     top_p=0.9,  # 控制输出的多样性，值越低输出越集中
#     max_tokens=512,  # 控制生成的最大token数量
#     frequency_penalty=0.5,  # 减少重复内容的生成
#     presence_penalty=0.5,  # 鼓励模型引入新内容
#     # stream=True
# )
#
# # 打印生成的回复
# print(completion.choices[0].message.content)

