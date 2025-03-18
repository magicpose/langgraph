#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os

from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from langgraph.func import entrypoint
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from langmem import create_manage_memory_tool, create_search_memory_tool

# Set up store and checkpointer
store = InMemoryStore()
llm = ChatOpenAI(model="AgentOS-Chat-72B")


def prompt(state):
    """Prepare messages with context from existing memories."""
    memories = store.search(
        ("memories",),
        query=state["messages"][-1].content,
    )
    system_msg = f"""You are a memory manager. Extract and manage all important knowledge, rules, and events using the provided tools.



Existing memories:
<memories>
{memories}
</memories>

Use the manage_memory tool to update and contextualize existing memories, create new ones, or delete old ones that are no longer valid.
You can also expand your search of existing memories to augment using the search tool."""
    return [{"role": "system", "content": system_msg}, *state["messages"]]


# Create the memory extraction agent
manager = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    prompt=prompt,
    tools=[
        # Agent can create/update/delete memories
        create_manage_memory_tool(namespace=("memories",)),
        create_search_memory_tool(namespace=("memories",)),
    ],
)


# Run extraction in background
@entrypoint(store=store)  # (1)
def app(messages: list):
    response = llm.invoke(
        [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            *messages,
        ]
    )

    # Extract and store triples (Uses store from @entrypoint context)
    manager.invoke({"messages": messages})
    return response


app.invoke(
    [
        {
            "role": "user",
            "content": "Alice manages the ML team and mentors Bob, who is also on the team.",
        }
    ]
)

print(store.search(("memories",)))

# [
#     Item(
#         namespace=["memories"],
#         key="5ca8dacc-7d46-40bb-9b3d-f4c2dc5c4b30",
#         value={"content": "Alice is the manager of the ML (Machine Learning) team"},
#         created_at="2025-02-11T00:28:01.688490+00:00",
#         updated_at="2025-02-11T00:28:01.688499+00:00",
#         score=None,
#     ),
#     Item(
#         namespace=["memories"],
#         key="586783fa-e501-4835-8651-028c2735f0d0",
#         value={"content": "Bob works on the ML team"},
#         created_at="2025-02-11T00:28:04.408826+00:00",
#         updated_at="2025-02-11T00:28:04.408841+00:00",
#         score=None,
#     ),
#     Item(
#         namespace=["memories"],
#         key="19f75f64-8787-4150-a439-22068b00118a",
#         value={"content": "Alice mentors Bob on the ML team"},
#         created_at="2025-02-11T00:28:06.951838+00:00",
#         updated_at="2025-02-11T00:28:06.951847+00:00",
#         score=None,
#     ),
# ]
