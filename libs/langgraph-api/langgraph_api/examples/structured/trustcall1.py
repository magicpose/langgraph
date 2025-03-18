#!/user/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint
from typing import List, Optional

from pydantic import BaseModel
from trustcall import create_extractor


class OutputFormat(BaseModel):
    preference: str
    sentence_preference_revealed: str


class TelegramPreferences(BaseModel):
    preferred_encoding: Optional[List[OutputFormat]] = None
    favorite_telegram_operators: Optional[List[OutputFormat]] = None
    preferred_telegram_paper: Optional[List[OutputFormat]] = None


class MorseCode(BaseModel):
    preferred_key_type: Optional[List[OutputFormat]] = None
    favorite_morse_abbreviations: Optional[List[OutputFormat]] = None


class Semaphore(BaseModel):
    preferred_flag_color: Optional[List[OutputFormat]] = None
    semaphore_skill_level: Optional[List[OutputFormat]] = None


class TrustFallPreferences(BaseModel):
    preferred_fall_height: Optional[List[OutputFormat]] = None
    trust_level: Optional[List[OutputFormat]] = None
    preferred_catching_technique: Optional[List[OutputFormat]] = None


class CommunicationPreferences(BaseModel):
    telegram: TelegramPreferences
    morse_code: MorseCode
    semaphore: Semaphore


class UserPreferences(BaseModel):
    communication_preferences: CommunicationPreferences
    trust_fall_preferences: TrustFallPreferences


class TelegramAndTrustFallPreferences(BaseModel):
    pertinent_user_preferences: UserPreferences


from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(model="moonshot-v1-32k")
llm = ChatOpenAI(model="DeepSeek-R1-Distill-Qwen-32B")
# llm = ChatOpenAI(model="gpt-4o-mini")
# llm = ChatOpenAI(model="AgentOS-Chat-72B")
# llm = ChatOpenAI(model="gpt-4o-mini")
bound = llm.with_structured_output(TelegramAndTrustFallPreferences)

conversation = """Operator: How may I assist with your telegram, sir?
Customer: I need to send a message about our trust fall exercise.
Operator: Certainly. Morse code or standard encoding?
Customer: Morse, please. I love using a straight key.
Operator: Excellent. What's your message?
Customer: Tell him I'm ready for a higher fall, and I prefer the diamond formation for catching.
Operator: Done. Shall I use our "Daredevil" paper for this daring message?
Customer: Perfect! Send it by your fastest carrier pigeon.
Operator: It'll be there within the hour, sir."""

# pprint(bound.invoke(f"""Extract the preferences from the following conversation:
# <convo>
# {conversation}
# </convo>"""))


import operator
from datetime import datetime
from typing import List

import pytz
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic.v1 import BaseModel, Field, validator
from typing_extensions import Annotated, TypedDict


class Preferences(BaseModel):
    foods: List[str] = Field(description="Favorite foods")

    @validator("foods")
    def at_least_three_foods(cls, v):
        if len(v) < 3:
            raise ValueError("Must have at least three favorite foods")
        return v


# llm = ChatOpenAI(model="moonshot-v1-32k")
llm = ChatOpenAI(model="moonshot-v1-32k")


def save_user_information(preferences: Preferences):
    """Save user information to a database."""
    return "User information saved"


def lookup_time(tz: str) -> str:
    """Lookup the current time in a given timezone."""
    try:
        # Convert the timezone string to a timezone object
        timezone = pytz.timezone(tz)
        # Get the current time in the given timezone
        tm = datetime.now(timezone)
        return f"The current time in {tz} is {tm.strftime('%H:%M:%S')}"
    except pytz.UnknownTimeZoneError:
        return f"Unknown timezone: {tz}"


# demo1
bound = llm.with_structured_output(TelegramAndTrustFallPreferences)


conversation = """Operator: How may I assist with your telegram, sir?
Customer: I need to send a message about our trust fall exercise.
Operator: Certainly. Morse code or standard encoding?
Customer: Morse, please. I love using a straight key.
Operator: Excellent. What's your message?
Customer: Tell him I'm ready for a higher fall, and I prefer the diamond formation for catching.
Operator: Done. Shall I use our "Daredevil" paper for this daring message?
Customer: Perfect! Send it by your fastest carrier pigeon.
Operator: It'll be there within the hour, sir."""

# pprint(bound.invoke(f"""Extract the preferences from the following conversation:
# <convo>
# {conversation}
# </convo>"""))


# demo2
bound = create_extractor(
    llm,
    tools=[TelegramAndTrustFallPreferences],
    tool_choice="TelegramAndTrustFallPreferences",
)

result = bound.invoke(
    f"""Extract the preferences from the following conversation:
<convo>
{conversation}
</convo>"""
)

print(result["responses"][0])


# demo3
class State(TypedDict):
    messages: Annotated[list, operator.add]


agent = create_extractor(llm, tools=[save_user_information, lookup_time])

builder = StateGraph(State)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode([save_user_information, lookup_time]))
builder.add_edge("tools", "agent")
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)

graph = builder.compile(checkpointer=MemorySaver())

# graph.get_graph().draw_mermaid_png(output_file_path='trustcall.png')

config = {"configurable": {"thread_id": "1234"}}
res = graph.invoke({"messages": [("user", "Hi there!")]}, config)
res["messages"][-1].pretty_print()

# res = graph.invoke(
#     {"messages": [("user", "Curious; what's the time in denver right now?")]}, config
# )
# res["messages"][-1].pretty_print()
