"""State management for the index graph."""
from typing import Annotated, Literal

from dataclasses import dataclass, field
from typing import Sequence

from langchain_core.messages import HumanMessage, BaseMessage
from typing_extensions import TypedDict

from anthropic import BaseModel
from pydantic import Field


class Content(TypedDict):
    plugin_id: str
    name: str
    desc: str
    inputs: dict


class Command(TypedDict):
    type: str
    content: Content


class InputState(TypedDict):
    shortcuts: list[Command]
    messages: list[BaseMessage]


class TriageState(TypedDict):
    question: str
    triage: str


class OutputState(TypedDict):
    question: str
    queries: list[str]
    reference: list
    raw_data: str
    ui_data: str
    final_answer: str


class GraphState(InputState):
    question: str
    queries: list[str]
    sql_res: dict
    perception: list
    reference: list
    knowledge: list
    raw_data: str
    ui_data: str
    final_answer: str


class ConfigSchema(TypedDict):
    db_conf: list
    doc_conf: list
    model: str
    mini_model: str
    embedding: str
    reason_model: str
    mini_reason_model: str


class RespondTo(BaseModel):
    logic: str = Field(
        description="logic on WHY the response choice is the way it is", default=""
    )
    response: Literal["search", "plan", "answer"] = "search"


class RespondRecommend(BaseModel):
    response: list[str] = Field(
        description="推荐的其他相关问题", default=[]
    )


class ResponseIdentify(BaseModel):
    identifier: str = Field(
        description="语义摘要标识，用来区分不通会话，20个字以内"
    )
