#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from langgraph.func import entrypoint
from langgraph.store.memory import InMemoryStore

from langmem import ReflectionExecutor, create_memory_store_manager

store = InMemoryStore()

# llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
llm = ChatOpenAI(model="AgentOS-Chat-72B")

# Create memory manager Runnable to extract memories from conversations
memory_manager = create_memory_store_manager(
    llm,
    # Store memories in the "memories" namespace (aka directory)
    namespace=("memories",),  #
)


@entrypoint(store=store)  # Create a LangGraph workflow
async def chat(message: str):
    response = llm.invoke(message)

    # memory_manager extracts memories from conversation history
    # We'll provide it in OpenAI's message format
    to_process = {"messages": [{"role": "user", "content": message}] + [response]}
    await memory_manager.ainvoke(to_process)  #
    return response.content


async def main():
    # Run conversation as normal
    response = await chat.ainvoke(
        "I like dogs. My dog's name is Fido.",
    )
    print(response)
    # Output: That's nice! Dogs make wonderful companions. Fido is a classic dog name. What kind of dog is Fido?

    # (in case our memory manager is still running)
    print(store.search(("memories",)))
    # [
    #     Item(
    #         namespace=["memories"],
    #         key="0145905e-2b78-4675-9a54-4cb13099bd0b",
    #         value={"kind": "Memory", "content": {"content": "User likes dogs as pets"}},
    #         created_at="2025-02-06T18:54:32.568595+00:00",
    #         updated_at="2025-02-06T18:54:32.568596+00:00",
    #         score=None,
    #     ),
    #     Item(
    #         namespace=["memories"],
    #         key="19cc4024-999a-4380-95b1-bb9dddc22d22",
    #         value={"kind": "Memory", "content": {"content": "User has a dog named Fido"}},
    #         created_at="2025-02-06T18:54:32.568680+00:00",
    #         updated_at="2025-02-06T18:54:32.568682+00:00",
    #         score=None,
    #     ),
    # ]

if __name__ == '__main__':
    asyncio.run(main())
