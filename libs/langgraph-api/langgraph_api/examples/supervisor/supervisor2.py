#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor

from langgraph.prebuilt import create_react_agent
from langgraph_api.examples.open_deep_research.langgraph.utils import google_search, deduplicate_and_format_sources

model = ChatOpenAI(model="AgentOS-Chat-72B")


def search(query_list: list):
    """网络搜索工具"""
    google_search(query_list)
    search_results = []
    source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000,
                                                include_raw_content=False)
    return source_str


research_agent = create_react_agent(
    model=model,
    tools=[search],
    name="web research",
    prompt="You are a web research"
)

research_team = create_supervisor(
    [research_agent],
    model=model,
).compile(name="research_team")

planning_agent = create_react_agent(
    model=model,
    tools=[],
    name="planning agent",
    prompt="You are a task planner"
)

planning_team = create_supervisor(
    [planning_agent],
    model=model,
).compile(name="planning_team")

top_level_supervisor = create_supervisor(
    [research_team, planning_team],
    model=model,
).compile(name="top_level_supervisor")

# Compile with checkpointer/store


async def main():
    async for msg in top_level_supervisor.astream(input={"messages": "西安明天天气怎么样?"}):
        print(msg)


if __name__ == '__main__':
    asyncio.run(main())
