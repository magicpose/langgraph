import json
from typing import TypedDict
from langgraph.graph import Graph, END, StateGraph
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import StateGraph
from langgraph_api.graph import PLUGINS
import asyncio
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def call_knowledge(question: str, config: RunnableConfig):
    file_ids = [file["fileId"] for file in json.loads(os.getenv("FILES"))]

    tool = PLUGINS["1900388850299637760"]

    payload = {
        "top": 100,
        "source": os.getenv("SOURCE"),
        "source_ids": file_ids,
        "query": f"{question}",
        "sub_service_code": os.getenv("SUB_SERVICE_CODE"),
        "service_code": os.getenv("SERVICE_CODE"),
        "langfuse_token": config["configurable"]["langfuse_token"]
    }

    output = await asyncio.to_thread(tool.forward, **payload)
    if output and json.loads(output)['code'] == 1:
        resp_json_data = json.loads(output).get("data")
    else:
        resp_json_data = None
    return resp_json_data


class DocState(TypedDict):
    queries: list[str]
    knowledge: list


async def search(state: DocState, config: RunnableConfig) -> DocState:
    questions = state.get("queries", [])

    results = [result for result in
               await asyncio.gather(*[call_knowledge(question, config) for question in questions])
               if result is not None and any(result)]

    # 使用字典去重，键为chunk_id，值为对应的项
    unique_items = {}
    for result_list in results:
        for item in result_list:
            chunk_id = item.get('chunk_id')  # 或者 item.chunk_id
            unique_items[chunk_id] = item

    # 转换回列表
    knowledge_results = list(unique_items.values())
    # 添加文档类型和
    file_list = json.loads(os.getenv("FILES"))
    file_map = {item['fileId']: item['fileName'] for item in file_list}

    for knowledge in knowledge_results:
        knowledge["id"] = knowledge["doc_id"]
        knowledge["type"] = "doc"
        knowledge["name"] = file_map.get(knowledge["source_id"])

    yield {
        "knowledge": knowledge_results
    }

workflow = StateGraph(DocState)

# 添加节点
workflow.add_node("search", search)

# 设置入口点
workflow.set_entry_point("search")

workflow.add_edge("search", END)

doc_graph = workflow.compile()


# async def main():
#
#
#     from langfuse.callback import CallbackHandler
#     langfuse_handler = CallbackHandler(
#         secret_key="sk-lf-6d9b5977-de5a-41bd-b41d-ae80c4f3d42d",
#         public_key="pk-lf-fc120dc9-46bf-4f83-a049-0fe659445881",
#         host="http://10.1.3.122:3005"
#     )
#     # 创建初始状态
#     state = {
#         "messages": [],
#         "question": ["你的测试问题1", "你的测试问题2"]  # 这里放入你要查询的问题
#     }
#
#
#
#     config = {"configurable": {"thread_id": "1111111112123"}, "recursion_limit": 20000000000,
#               "callbacks": [langfuse_handler]}
#     # 运行图
#     result = await kw_graph.ainvoke(state, config=config)
#     return result
#
#
# if __name__ == '__main__':
#     # 运行主函数
#     result = asyncio.run(main())
#     print("结果:", result)
