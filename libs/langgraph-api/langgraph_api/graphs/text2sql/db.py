import json
import operator
from typing import Dict, TypedDict, Annotated, Sequence, Optional
from langgraph.graph import Graph, END, StateGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.managed import RemainingSteps
from openai import OpenAI
from langgraph.graph.state import StateGraph
from langgraph_api.graph import PLUGINS
from langgraph_api.graphs.text2sql.tools import search_atlas as search_atlas_data, run_sql, search_database as search_database_data
import os
import logging

from langgraph_api.graphs.text2sql.evaluation_guard import build_evaluation_prompt, build_question_prompt, \
    ValidationResult

from langgraph_api.graphs.text2sql.sql_base import SqlBase

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

debug = False

client = OpenAI(
     api_key=os.getenv("OPENAI_API_KEY"),
     base_url=os.getenv("OPENAI_API_BASE")
)


class DbState(TypedDict):
    messages: list[BaseMessage]
    db_messages: Annotated[list, operator.add]
    remaining_steps: RemainingSteps
    database_id: str
    database_name: str
    database_type: str
    question: str
    merged: str
    milvus: dict
    sql: str
    reflect_sql: str
    execute_sql: str
    sql_res: str
    atlas: dict
    evaluation: dict
    history_prompt: list
    retry_attempt: int


# async def tool_action(state: AgentState, config: RunnableConfig):
#     # 参数
#     tool = PLUGINS[state["action"]["plugin_id"]]
#     args = state["args"]
#     args.setdefault("langfuse_token", config["configurable"]["langfuse_token"])
#     output = tool.forward(**args)
#     raw_data = json.loads(output).get("data") if output else None
#
#     yield {"raw_data": raw_data}


async def search_database(state: DbState, config: RunnableConfig):
    logger.info(f"✅ step : search_database")
    database = json.loads(os.getenv("DATABASE_CONF"))
    # state["question"] = state["messages"][0].get("content")

    yield {
        "question": state["messages"][0].get("content"),
        "database_id": database.get("database_id", ""),
        "database_name": database.get("database_name", ""),
        "database_type": database.get("database_type", ""),
        "retry_attempt": 0
    }


async def search_milvus(state: DbState, config: RunnableConfig):
    question = state.get("question", "")

    # 检索向量库
    tool = PLUGINS["1900388813788221441"]
    payload = {
        "dataSourceId": state.get("database_id"),
        "databaseName": state.get("database_name"),
        "message": question,
        "langfuse_token": config["configurable"]["langfuse_token"]
    }

    ddl = None

    output = tool.forward(**payload)
    if output and json.loads(output)['code'] == 1:
        ddl = json.loads(output).get("data")

    # data = search_milvus_data(question,state.get("database_id", ""))

    data = {
        "question": [],
        "doc": [],
        "ddl": [ddl] if ddl else [],
    }

    yield {
        "milvus": data,
    }


async def search_atlas(state: DbState):
    logger.info(f"✅ step : search_atlas")

    question = state.get("question", "")

    data = search_atlas_data(question, state.get("database_id", ""))

    yield {
        "atlas": data,
    }


async def merge(state: DbState):
    pass


async def route_after_merge(state: DbState):
    milvus = state.get("milvus")
    atlas = state.get("atlas")

    if any(milvus.get("ddl", [])) or any(atlas.get("ddl", [])):
        return "generate_sql"
    else:
        return "db_answer"


async def generate_sql(state: DbState):
    logger.info(f"✅ step : generate_sql")
    question = state.get("question", "")
    milvus = state.get("milvus")
    atlas = state.get("atlas")

    merged = {key: milvus[key] + atlas[key] for key in milvus.keys()}

    base = SqlBase(client=client,
                model="qwen2.5-72b-instruct",
                metadata=merged,
                config={"dialect": state.get("database_type")},
                debug=debug)

    sql = base.generate_sql(question)
    history_prompt = base.history_prompt

    yield {
        "sql": sql,
        "merged": merged,
        "history_prompt": history_prompt,
        "db_messages": [history_prompt],
    }


async def execute(state: DbState):
    logger.info(f"✅ step : execute_sql")

    sql = state.get("execute_sql") or state.get("sql")
    logger.info(f"execute_sql sql :{sql}")

    tool = PLUGINS["1900388813784027136"]
    payload = {
        "id": state.get("database_id"),
        "sql": sql,
        'pageNo': '1',
        'pageSize': '10',
        'source': '0'
    }

    output = tool.forward(**payload)
    response = json.loads(output) if output else None

    # 检查响应
    if response and response['code'] == 1 and response['data']['code'] == 1:
        sql_res = response['data']['data']['data']['records']
    elif response['data'] is not None:
        if response['data'].get('data'):
            sql_res = response['data']['data'].get('msg')
        else:
            sql_res = response['data'].get('msg')
    else:
        sql_res = 'sql执行失败'

    # sql_res = run_sql(sql =sql, database_id=state.get("database_id", ""))

    logger.info(f"execute_sql sql_res :{sql_res}")

    yield {
        "sql": sql,
        "sql_res": sql_res
    }


async def evaluate(state: DbState):
    logger.info(f"✅ step : evaluate")
    merged = state.get("merged")
    sql = state.get("sql")
    sql_res = state.get("sql_res")
    question = state.get("question", "")

    base = SqlBase(metadata=merged)
    messages = []

    evaluation_prompt_system = build_evaluation_prompt(state.get("database_type"), base.get_related_ddl(), base.get_related_documentation())
    logger.info(f"评估 prompt_system：{evaluation_prompt_system}")
    messages.append({"role": "system", "content": evaluation_prompt_system})

    evaluation_prompt_user = build_question_prompt(question, sql, sql_res)
    logger.info(f"评估 prompt_user：{evaluation_prompt_user}")
    messages.append({"role": "user", "content": evaluation_prompt_user})

    response = client.chat.completions.create(
        model="Hs-Deepseek-v3",
        # model="qwen2.5-72b-instruct",
        messages=[{"role": "system", "content": evaluation_prompt_system},
                  {"role": "user", "content": evaluation_prompt_user}],
        stop=None,
        temperature=0.6
    )

    # if hasattr(response.choices[0].message, 'reasoning_content') and response.choices[0].message.reasoning_content:
    #     logger.info(f"评估 思考过程：{response.choices[0].message.reasoning_content}")
    #     messages.append({"role": "assistant", "content": response.choices[0].message.reasoning_content})

    if response.choices[0].message.content:
        logger.info(f"评估 结果：{response.choices[0].message.content}")
        messages.append({"role": "assistant", "content": response.choices[0].message.content})

    evaluation = ValidationResult.from_json(response.choices[0].message.content)

    logger.info(f"评估 结果-ValidationResult：{str(evaluate)}")

    yield {
        "db_messages": [*state["db_messages"], *messages],
        "evaluation": evaluation,
        "retry_attempt": state.get("retry_attempt") + 1
    }


async def reflect(state: DbState):
    logger.info(f"✅ step : reflect")

    evaluation = state.get("evaluation")

    history_prompt = state.get("history_prompt", [])

    messages = history_prompt

    if evaluation.suggestions:
        user_str = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(evaluation.suggestions))
        user_str = f"请按照建议重新生成sql,建议是：{user_str}"
        history_prompt.append({"role": "user", "content": user_str})
        messages.append({"role": "user", "content": user_str})

        logger.info(f"reflect  user_str:{user_str}")
        logger.info(f"reflect  history_prompt:{history_prompt}")

    response = client.chat.completions.create(
        model="Hs-Deepseek-v3",
        messages=history_prompt,
        stop=None,
        temperature=0,
    )

    if hasattr(response.choices[0].message, 'reasoning_content') and response.choices[0].message.reasoning_content is not None:
        logger.info(f"reflect  反思的思考过程:{response.choices[0].message.reasoning_content}")
        messages.append({"role": "assistant", "content": response.choices[0].message.reasoning_content})

    if response.choices[0].message.content is not None:
        logger.info(f"reflect  反思的结果:{response.choices[0].message.content}")
        messages.append({"role": "assistant", "content": response.choices[0].message.content})

    base = SqlBase()
    reflect_sql = base.extract_sql(response.choices[0].message.content)

    logger.info(f"reflect  抽取sql结果:{reflect_sql}")

    yield {
        "db_messages": [*state["messages"], *messages]
    }


async def route_after_evaluate(state: DbState):

    evaluation = state.get("evaluation")

    if ((evaluation.overall.is_pass and evaluation.overall.score > 0.7)
            or state.get("retry_attempt") > 3):
        return "db_answer"

    return "reflect"


async def db_answer(state: DbState):
    yield {
        "sql_res": {
            "database_id": state.get("database_id"),
            "database_name": state.get("database_name"),
            "database_type": state.get("database_type"),
            "final_sql": state.get("sql"),
            "final_sql_res": state.get("sql_res"),
            "type": "db",
        }
    }



# 添加条件路由：execute_sql → evaluate 或 END
async def route_after_execute(state: DbState):
    # 检查是否来自反思节点（通过 retry_attempt 标志判断）
    return "db_answer" if state.get("retry_attempt") > 3 else "evaluate"


db = StateGraph(DbState)

# 添加节点
db.add_node(search_database)
db.add_node(search_milvus)
db.add_node(search_atlas)
db.add_node(merge)
db.add_node(generate_sql)
db.add_node(execute)
db.add_node(evaluate)
db.add_node(reflect)
db.add_node(db_answer)

# 设置入口点
db.set_entry_point("search_database")
# 添加边 - 定义节点间的连接关系
db.add_edge("search_database", "search_milvus")
db.add_edge("search_database", "search_atlas")
db.add_edge("search_milvus", "merge")
db.add_edge("search_atlas", "merge")
# workflow.add_edge("merge", "generate_sql")
db.add_conditional_edges("merge", route_after_merge)
db.add_edge("generate_sql", "execute")
db.add_edge("reflect", "execute")
db.add_edge("db_answer", END)

db.add_conditional_edges("evaluate", route_after_evaluate)

db.add_conditional_edges("execute", route_after_execute)

db_graph = db.compile()

# graph.get_graph().draw_mermaid_png(output_file_path="text2sql.png")
