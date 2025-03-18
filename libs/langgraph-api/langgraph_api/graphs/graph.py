#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import uuid
from datetime import datetime

from typing import Literal, Any

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from sdk.skillcore import UiDataRequest

from langgraph.constants import END
from langgraph.graph.state import StateGraph
from langgraph.prebuilt.interrupt import HumanInterrupt
from langgraph.types import interrupt, Command, Send
from langgraph_api.graph import PLUGINS
from langgraph_api.graphs.knowledge.graph import doc_graph
from langgraph_api.graphs.state import RespondTo, ConfigSchema, GraphState, RespondRecommend, ResponseIdentify, \
    InputState, TriageState, OutputState
from langgraph_api.graphs.text2sql.db import db_graph
from langgraph_api.http_utils import get_skill_client


async def tool_action(state: GraphState, config: RunnableConfig):
    # 参数
    tool = PLUGINS[state["action"]]
    args = state["args"]
    args.setdefault("langfuse_token", config["configurable"]["langfuse_token"])
    output = tool.forward(**args)
    raw_data = json.loads(output).get("data") if output else None

    yield {"raw_data": raw_data}

    if raw_data:
        # gen ui
        client = get_skill_client()
        req = UiDataRequest(data=raw_data, prompt="")
        ui_data = client.get_ui_data(req)

        yield {"ui_data": ui_data}


async def tool_input(state: GraphState, config: RunnableConfig) -> (
        Literal)["human_node", "tool_action"]:
    plugin = state.get("shortcuts")[0]["content"]
    plugin_id = plugin["plugin_id"]

    # input = plugin["inputs"]
    # # 将指令列表数据转换为技能参数

    # 通过模型做参数提取
    detail = get_skill_client().skill_detail(plugin_id).data

    # 参数不够，返回前端中断
    request: HumanInterrupt = {
        "action_request": {"action": plugin_id, "args": detail.get("content")},
        "config": {
            "allow_ignore": True,
            "allow_respond": True,
            "allow_edit": True,
            "allow_accept": True,
        },
        "description": plugin["desc"],
    }

    feedback = interrupt([request])

    if feedback["type"] == "edit":
        args = feedback["args"]
        return Send("tool_action", arg=args)
    elif feedback["type"] == "false":
        return Send("answer", state)
    else:
        raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")


async def answer(state: GraphState, config: RunnableConfig):
    # 进行总结输出
    print(f"#################{state}")
    # model = config["configurable"].get("model", "deepseek-ai/DeepSeek-V3")
    model = config["configurable"].get("model", "Qwen2.5-72B-Instruct-AWQ")
    llm = ChatOpenAI(model=model, temperature=0.6)
    prompt_config = config["configurable"]
    reference = state.get("perception")
    input_message = answer_prompt.format(
        question=state.get("messages")[0]["content"] if state.get("messages") else "",
        # skill=f"[page 1 begin]{state.get('raw_data') or ''}[page 1 end]",
        reference=reference,
        cur_date=datetime.now()
    )
    response = await llm.ainvoke(input_message)

    yield {"final_answer": response}


async def recommend(state: GraphState, config: RunnableConfig):
    # 根据历史上下文进行推荐
    model = config["configurable"].get("model", "moonshot-v1-32k")
    llm = ChatOpenAI(model=model, temperature=0.6)
    prompt_config = config["configurable"]
    input_message = recommend_prompt.format(
        question=state.get("messages")[0]["content"] if state.get("messages") else "",
        cur_date=datetime.now(),
        black_list=prompt_config.get("black_list", []),
        content=state
    )
    model = llm.with_structured_output(RespondRecommend)
    response = await model.ainvoke(input_message)

    yield {"recommend": response}


async def identify(state: GraphState, config: RunnableConfig):
    model = config["configurable"].get("model", "moonshot-v1-8k")
    llm = ChatOpenAI(model=model, temperature=0)
    prompt_config = config["configurable"]
    input_message = identify_prompt.format(
        question=state.get("messages")[0]["content"] if state.get("messages") else "",
        cur_time=datetime.now(),
        answer=state.get("final_answer")
    )
    model = llm.with_structured_output(ResponseIdentify)
    response = await model.ainvoke(input_message)

    yield {"identifier": response}


async def human_node(state: GraphState):
    pass


triage_prompt = """
# 角色
你是一个专业的意图识别助手。任务是分析用户输入的文本，准确判断其核心意图，并用简洁的语言描述。
先简要分析文本内容，再准确判断核心意图。

# 规则
输入普通的问候语或闲聊，如“你好”等，直接回答路由到 answer。
如果问题没有合适的技能来完成，通过搜索相关知识完成任务，选择 search；
如果问题有符合的技能，需要进行详细的规划，则选择 plan。
- search：没有合适技能来调用，需要通过搜索完成任务。
- plan：代表你需要进行规划，通过搜索，调用技能等完成复杂任务。
- answer：非常简单的问候，例如你好，你只需要根据模型回答问题。

# 输出格式，要求只输出类型：
- search 
- plan
- answer

# 以下是你可以用到的技能：
{skills}

用户输入的消息如下：
{input}
"""

answer_prompt = """# 以下内容是基于用户发送的消息的搜索结果:
{reference}
在我给你的搜索结果中，每个结果都是[page X begin]...[page X end]格式的，X代表每篇文章的数字索引。请在适当的情况下在句子末尾引用上下文。请按照引用编号[citation:X]的格式在答案中对应部分引用上下文。如果一句话源自多个上下文，请列出所有相关的引用编号，例如[citation:3][citation:5]，切记不要将引用集中在最后返回引用编号，而是在答案对应部分列出。
如果没有搜索结果则不需要返回数字索引的格式
在回答时，请注意以下几点：
- 今天是{cur_date}。
- 并非搜索结果的所有内容都与用户的问题密切相关，你需要结合问题，对搜索结果进行甄别、筛选。
- 对于列举类的问题（如列举所有航班信息），尽量将答案控制在10个要点以内，并告诉用户可以查看搜索来源、获得完整信息。优先提供信息完整、最相关的列举项；如非必要，不要主动告诉用户搜索结果未提供的内容。
- 对于创作类的问题（如写论文），请务必在正文的段落中引用对应的参考编号，例如[citation:3][citation:5]，不能只在文章末尾引用。你需要解读并概括用户的题目要求，选择合适的格式，充分利用搜索结果并抽取重要信息，生成符合用户要求、极具思想深度、富有创造力与专业性的答案。你的创作篇幅需要尽可能延长，对于每一个要点的论述要推测用户的意图，给出尽可能多角度的回答要点，且务必信息量大、论述详尽。
- 如果回答很长，请尽量结构化、分段落总结。如果需要分点作答，尽量控制在5个点以内，并合并相关的内容。
- 对于客观类的问答，如果问题的答案非常简短，可以适当补充一到两句相关信息，以丰富内容。
- 你需要根据用户要求和回答内容选择合适、美观的回答格式，确保可读性强。
- 你的回答应该综合多个相关来源回答，不能重复引用一个来源。
- 除非用户要求，否则你回答的语言需要和用户提问的语言保持一致。

# 用户消息为：
{question}
"""

recommend_prompt = """
# 角色
根据上下文消息，输出其他推荐问题

# 推荐逻辑框架
用户问题: {question},
场景信息: 当前时间:{cur_date}, 设备:PC,
情感分析: 积极,
推荐策略: 
  核心问题延伸,
  个性化场景推荐
多模态交互:
  输出可以包含一些表情
  
风险控制: 
  屏蔽列表:{black_list}
  情感过滤:负面情绪时禁用营销内容
  时效性检查:过时内容自动归档

多模态交互:
  
反馈机制:

# 内容规则
  避免重复推荐相关内容
  直接输出问题，不要包含思考内容
  推荐不超过3-5条

# 上下文信息如下
{content}
"""

identify_prompt = """
# 角色
总结用户上下文内容的摘要，用来标识当前对话
# 要求
20字以内，突出用户输入，只提取输出内容的关键信息。
# 上下文信息如下
用户输入：{question}
当前时间：{cur_time}
输出：{answer}
"""


async def search(state: TriageState):
    # yield Send("db_search", state)
    # yield Send("generate_queries", state)
    pass


def route_after_triage(
    state: GraphState,
) -> Literal["command", "search", "plan", "answer"]:
    if state["triage"].response == "command":
        return "command"
    elif state["triage"].response == "plan":
        # todo 临时修改策略
        return "search"
    elif state["triage"].response == "search":
        return "search"
    elif state["triage"].response == "answer":
        return "answer"
    else:
        raise ValueError


async def command(state: GraphState):
    pass


async def plan(state: GraphState):
    pass


async def generate_queries(state: TriageState):
    template = """你是一个人工智能语言模型助手。你的任务是生成三个不同的版本的给定用户问题，以便从向量数据库中检索相关文档。
    通过从多个角度生成用户问题，你的目标是帮助用户克服基于距离的相似性搜索的一些限制。请将这些替代问题用换行符分隔 {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI

    generate_queries = (
            prompt_perspectives
            | ChatOpenAI(model='moonshot-v1-8k', temperature=0)
            | StrOutputParser()
            | (lambda x: x.split("\n"))
    )

    yield {
        "queries": await generate_queries.ainvoke(input=state.get("question"))
    }


async def flow_action(state: GraphState):
    pass


async def triage_input(state: InputState, config: RunnableConfig) -> TriageState:
    # 用户输入意图识别
    response = RespondTo()

    if state.get("shortcuts") and len(state.get("shortcuts")) == 1:
        response.response = "command"
    else:
        # 通过轻量模型判断意图识别
        model = config["configurable"].get("model", "moonshot-v1-8k")
        llm = ChatOpenAI(model=model, temperature=0)
        prompt_config = config["configurable"]
        # 技能来自于传入指令和 模糊搜索到的指令

        input_message = triage_prompt.format(
            input=state.get("messages"),
            # skills="\n".join(value.__doc__ for value in PLUGINS.values())
            skills=""
        )
        model = llm.with_structured_output(RespondTo)
        response = await model.ainvoke(input_message)

    yield {
        "triage": response,
        "question": state.get("messages")[0].get("content"),
    }


async def route_after_command(
        state: GraphState) -> Literal["tool_input", "flow_action", "doc_search", "db_search", "answer"]:
    # 指令进行分类
    commands = state.get("shortcuts")
    if not commands:
        return "answer"
    elif commands[0]["type"] == "plug":
        return "tool_input"
    elif commands[0]["type"] == "flow":
        return "flow_action"
    elif commands[0]["type"] == "doc_search":
        return "doc_search"
    elif commands[0]["type"] == "db_search":
        return "db_search"
    else:
        raise ValueError


async def route_after_tool(
        state: GraphState) -> Literal["answer"]:
    if state["triage"].response == "answer":
        return "answer"
    else:
        raise ValueError


async def enter_after_human(
        state: GraphState) -> Literal["tool_action", "answer"]:
    return "answer"


async def guard(state: GraphState, config: RunnableConfig):
    pass


async def get_reranked_docs(rerank_list, doc_res):
    if not rerank_list:
        return []
    # 获取rerank_list中的所有index
    indices = [item["index"] for item in rerank_list]

    # 创建新的doc_res列表，按照indices中的顺序排列
    new_doc_res = []
    for idx in indices:
        if 0 <= idx < len(doc_res):
            # 将原始文档添加到新列表中
            new_doc_res.append(doc_res[idx])

    return new_doc_res


async def rerank(state: GraphState):
    # 组装 感知源信息 [page X begin]...[page X end]格式的，X代表每个感知源的数字索引
    doc_res = state.get("knowledge", [])
    db_res = state.get("sql_res", {})

    tool = PLUGINS["1900388813674975232"]

    documents = [item["text"] for item in doc_res if item["text"] is not None]

    formatted_texts = []
    reranked_docs = []

    if documents:
        payload = {
            "model": "bce-reranker-base_v1",
            "documents": documents,
            # "query": "\n".join(state.get("queries")),
            "query": state.get("messages")[0].get("content"),
            "top_n": 5,
        }

        output = await asyncio.to_thread(tool.forward, **payload)
        rerank_list = []

        if output and json.loads(output)['code'] == 1:
            data = json.loads(output).get("data")
            rerank_list = data.get("results") if data else []

        reranked_docs = await get_reranked_docs(rerank_list, doc_res)
        if reranked_docs and any(reranked_docs):
            for i, doc in enumerate(reranked_docs, 1):  # 从1开始计数
                if "text" in doc and doc["text"] is not None:
                    # 提取text内容并按指定格式组装
                    text_content = doc["text"]
                    formatted_text = f"[page {i} begin]{text_content}[page {i} end]"
                    formatted_texts.append(formatted_text)

        if db_res.get("final_sql_res"):
            formatted_texts.append(f"[page {len(reranked_docs)+1} begin]{db_res.get('final_sql_res')}[page {len(reranked_docs)+1} end]")

    reranked_docs.append(db_res)

    yield {
        'reference': reranked_docs,
        'perception': formatted_texts
    }

workflow = StateGraph(GraphState, input=InputState, output=OutputState, config_schema=ConfigSchema)
# Define the nodes
workflow.add_node(triage_input)
workflow.add_node(plan)
workflow.add_node(tool_input)
workflow.add_node(tool_action)
workflow.add_node(flow_action)
workflow.add_node(human_node)
workflow.add_node(generate_queries)
workflow.add_node(search)
# db_graph = db_graph.with_config(input_keys=["question"], output_keys=["sql_res"])
workflow.add_node("db_search", db_graph)
workflow.add_node("doc_search", doc_graph)
workflow.add_node(command)
workflow.add_node(rerank)
workflow.add_node(answer)
workflow.add_node(recommend)
workflow.add_node(identify)

# Build graph
workflow.set_entry_point("triage_input")
workflow.add_conditional_edges("triage_input", route_after_triage)
workflow.add_conditional_edges("command", route_after_command)
workflow.add_edge("plan", "answer")
workflow.add_edge("flow_action", "answer")
workflow.add_edge("search", "generate_queries")
workflow.add_edge("search", "db_search")
workflow.add_edge("generate_queries", "doc_search")
workflow.add_edge(["doc_search", "db_search"], "rerank")
workflow.add_edge("tool_action", "answer")
workflow.add_edge("rerank", "answer")
workflow.add_edge("answer", "recommend")
workflow.add_edge("recommend", "identify")
# workflow.add_edge("recommend", END)
workflow.add_edge("identify", END)

graph = workflow.compile()

# graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
