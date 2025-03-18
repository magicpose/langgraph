#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from pprint import pprint

from langchain_openai import ChatOpenAI

from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

model = ChatOpenAI(model="AgentOS-Chat-72B")
# model = ChatOpenAI(model="moonshot-v1-8k")
# model = ChatOpenAI(model="deepseek-ai/DeepSeek-V3")
# model = ChatOpenAI(model="gpt-4o")
# model = ChatOpenAI(model="AgentOS-Chat-72B", stream_options={"include_usage": True})

# Create specialized agents


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def web_search(query: str) -> str:
    """Search the web for information."""
    return (
        "Here are the headcounts for each of the FAANG companies in 2024:\n"
        "1. **Facebook (Meta)**: 67,317 employees.\n"
        "2. **Apple**: 164,000 employees.\n"
        "3. **Amazon**: 1,551,000 employees.\n"
        "4. **Netflix**: 14,000 employees.\n"
        "5. **Google (Alphabet)**: 181,269 employees."
    )

math_agent = create_react_agent(
    model=model,
    tools=[add, multiply],
    name="math_expert",
    prompt="You are a math expert. Always use one tool at a time."
)


research_agent = create_react_agent(
    model=model,
    tools=[web_search],
    name="research_expert",
    prompt="You are a world class researcher with access to web search. Do not do any math."
)


async def main():
    # Create supervisor workflow
    workflow = create_supervisor(
        [research_agent, math_agent],
        model=model,
        prompt=(
            "You are a team supervisor managing a research expert and a math expert. "
            "For current events, use research_agent. "
            "For math problems, use math_agent."
        ),
        output_mode="last_message"
    )

    # Compile and run
    app = workflow.compile()

    # research_team = create_supervisor(
    #     [research_agent, math_agent],
    #     model=model,
    # ).compile(name="research_team")
    #
    # writing_team = create_supervisor(
    #     [writing_agent, publishing_agent],
    #     model=model,
    # ).compile(name="writing_team")
    #
    # top_level_supervisor = create_supervisor(
    #     [research_team, writing_team],
    #     model=model,
    # ).compile(name="top_level_supervisor")

    # "values", "messages", "updates", "events", "debug", "custom", "messages-tuple"
    for msg in app.stream(input={
        "messages": [
            {
                "role": "user",
                "content": "2024 年 FAANG 这几家公司的总员工人数是多少?"
            }
        ]
    }):
        # if msg["event"] == "on_chat_model_stream":
        #     print(msg["data"]["chunk"].content, end="", flush=True)
        pprint(msg)

    # workflow = create_supervisor(
    #     agents=[agent1, agent2],
    #     output_mode="full_history"
    # )
    #
    # workflow = create_supervisor(
    #     agents=[agent1, agent2],
    #     output_mode="last_message"
    # )


if __name__ == '__main__':
   asyncio.run(main())
