from typing import TypedDict
from langgraph_sdk import get_client
import httpx
import uuid
import hashlib
from langgraph.graph import StateGraph, START, END

client = get_client()


class JobKickoff(TypedDict):
    minutes_since: int


async def main(config):
    # minutes_since: int = state["minutes_since"]

    thread_id = str(
        uuid.UUID(hex=hashlib.md5('123'.encode("UTF-8")).hexdigest())
    )
    # try:
    #     thread_info = await client.threads.get(thread_id)
    # except Exception as e:
    #     raise e
    #
    # await client.threads.update(thread_id, metadata={"email_id": '123'})

    # await client.runs.create(
    #     thread_id,
    #     "main",
    #     input={"email": {}},
    #     multitask_strategy="rollback",
    # )
    print(f'【config】 :{config}')


graph = StateGraph(JobKickoff)
graph.add_node(main)
graph.add_edge(START, "main")
graph.add_edge("main", END)
graph = graph.compile()
