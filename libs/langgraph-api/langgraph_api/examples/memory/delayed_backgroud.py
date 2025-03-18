#!/user/bin/env python3
# -*- coding: utf-8 -*-
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from langgraph.func import entrypoint
from langgraph.store.memory import InMemoryStore
from langmem import ReflectionExecutor, create_memory_store_manager


llm = ChatOpenAI(model="AgentOS-Chat-72B")

# Create memory manager to extract memories from conversations
memory_manager = create_memory_store_manager(
    llm,
    namespace=("memories",),
)
# Wrap memory_manager to handle deferred background processing
executor = ReflectionExecutor(memory_manager)
store = InMemoryStore()


@entrypoint(store=store)
def chat(message: str):
    response = llm.invoke(message)
    # Format conversation for memory processing
    # Must follow OpenAI's message format
    to_process = {"messages": [{"role": "user", "content": message}] + [response]}

    # Wait 30 minutes before processing
    # If new messages arrive before then:
    # 1. Cancel pending processing task
    # 2. Reschedule with new messages included
    delay = 0.5 # In practice would choose longer (30-60 min)
    # depending on app context.
    executor.submit(to_process, after_seconds=delay)
    return response.content


if __name__ == '__main__':
    for msg in chat.stream("你好"):
        print(msg)


