#!/user/bin/env python3
# -*- coding: utf-8 -*-
from anthropic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from langgraph.func import entrypoint
from langgraph.store.memory import InMemoryStore
from langmem import create_memory_store_manager


class Triple(BaseModel): #
    """Store all new facts, preferences, and relationships as triples."""
    subject: str
    predicate: str
    object: str
    context: str | None = None


# Set up store and models
store = InMemoryStore() #
manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest",
    namespace=("chat", "{user_id}", "triples"),
    schemas=[Triple],
    instructions="Extract all user information and events as triples.",
    enable_inserts=True,
    enable_deletes=True,
)
llm = ChatOpenAI(model="AgentOS-Chat-72B")


# Define app with store context
@entrypoint(store=store) #
def app(messages: list):
    response = llm.invoke(
        [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            *messages
        ]
    )

    # Extract and store triples (Uses store from @entrypoint context)
    manager.invoke({"messages": messages})
    return response


# First conversation
app.invoke(
    [
        {
            "role": "user",
            "content": "Alice manages the ML team and mentors Bob, who is also on the team.",
        },
    ],
    config={"configurable": {"user_id": "user123"}},
)

# Second conversation
app.invoke(
    [
        {"role": "user", "content": "Bob now leads the ML team and the NLP project."},
    ],
    config={"configurable": {"user_id": "user123"}},
)

# Third conversation
app.invoke(
    [
        {"role": "user", "content": "Alice left the company."},
    ],
    config={"configurable": {"user_id": "user123"}},
)

# Check stored triples
for item in store.search(("chat", "user123")):
    print(item.namespace, item.value)

# Output:
# ('chat', 'user123', 'triples') {'kind': 'Triple', 'content': {'subject': 'Bob', 'predicate': 'is_member_of', 'object': 'ML_team', 'context': None}}
# ('chat', 'user123', 'triples') {'kind': 'Triple', 'content': {'subject': 'Bob', 'predicate': 'leads', 'object': 'ML_team', 'context': None}}
# ('chat', 'user123', 'triples') {'kind': 'Triple', 'content': {'subject': 'Bob', 'predicate': 'leads', 'object': 'NLP_project', 'context': None}}
# ('chat', 'user123', 'triples') {'kind': 'Triple', 'content': {'subject': 'Alice', 'predicate': 'employment_status', 'object': 'left_company', 'context': None}}