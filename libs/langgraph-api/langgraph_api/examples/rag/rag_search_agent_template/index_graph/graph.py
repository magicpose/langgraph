"""This "graph" simply exposes an endpoint for a user to upload docs to be indexed."""
import asyncio
import json
from typing import Optional

from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph_api.examples.rag.rag_search_agent_template.index_graph.configuration import IndexConfiguration
from langgraph_api.examples.rag.rag_search_agent_template.index_graph.state import IndexState
from langgraph_api.examples.rag.rag_search_agent_template.shared import retrieval
from langgraph_api.examples.rag.rag_search_agent_template.shared.state import reduce_docs


async def index_docs(
    state: IndexState, *, config: Optional[RunnableConfig] = None
) -> dict[str, str]:
    """Asynchronously index documents in the given state using the configured retriever.

    This function takes the documents from the state, ensures they have a user ID,
    adds them to the retriever's index, and then signals for the documents to be
    deleted from the state.

    If docs are not provided in the state, they will be loaded
    from the configuration.docs_file JSON file.

    Args:
        state (IndexState): The current state containing documents and retriever.
        config (Optional[RunnableConfig]): Configuration for the indexing process.r
    """
    if not config:
        raise ValueError("Configuration required to run index_docs.")

    configuration = IndexConfiguration.from_runnable_config(config)
    docs = state.docs
    if not docs:
        with open(configuration.docs_file) as f:
            serialized_docs = json.load(f)
            docs = reduce_docs([], serialized_docs)

    with retrieval.make_retriever(config) as retriever:
        await retriever.aadd_documents(docs)

    return {"docs": "delete"}


# Define the graph
builder = StateGraph(IndexState, config_schema=IndexConfiguration)
builder.add_node(index_docs)
builder.add_edge(START, "index_docs")
builder.add_edge("index_docs", END)
# Compile into a graph object that you can invoke and deploy.

from langfuse.callback import CallbackHandler

# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler(
    secret_key="sk-lf-45977ced-899f-41a4-bd99-2aa48b5f6988",
    public_key="pk-lf-a8db51d2-7534-4218-98bc-7af2d9651e04",
    host="http://10.1.3.122:3005"
)

memory = MemorySaver()

thread_config = {"configurable": {"thread_id": "1234"}, 'callbacks': [langfuse_handler]}


graph = builder.compile(checkpointer=memory)
graph.name = "IndexGraph"

# graph.get_graph().draw_mermaid_png(output_file_path='index.png')

from langchain_core.documents import Document
doc = Document("""LangGraph 是一个用于构建和运行图计算的框架。以下从它的概念、特点、应用场景等方面为你进行介绍：
概念
LangGraph 是在人工智能领域，尤其是结合了语言模型和图计算相关的一种框架。它可以用于构建复杂的图结构，帮助处理各种基于图的任务，比如知识图谱构建、图数据分析、图神经网络应用等。通过 LangGraph，开发者能够以一种相对高效、灵活的方式定义图的结构、节点和边的属性以及它们之间的交互规则等。
特点
模块化设计 ：它通常采用模块化的架构，使得开发者可以方便地添加、修改或替换图的各个组成部分，比如节点处理模块、边的更新规则模块等，从而能够根据具体的任务需求灵活定制图计算流程。
与语言模型的良好结合 ：能够和先进的语言模型相互配合，利用语言模型强大的文本理解和生成能力，对图中的节点信息（如节点的文本描述等）进行处理，或者根据图的结构和内容生成相关的文本输出，拓展了图计算在自然语言处理相关任务中的应用。
高效的图计算能力 ：提供了优化的计算机制，可以高效地处理大规模的图数据，包括快速的图遍历、图更新以及复杂的图算法实现等，保证在处理复杂图任务时有较好的性能表现。
应用场景
知识图谱构建与应用 ：可用于构建知识图谱，将各种实体（如人物、地点、概念等）作为节点，实体之间的关系作为边，通过 LangGraph 来整合、更新和查询知识图谱中的信息。例如在智能问答系统中，根据用户的问题在知识图谱中进行图遍历和推理，给出准确的答案。
社交网络分析 ：分析社交网络中的用户关系图，挖掘用户群体的特征、影响力传播路径等。比如通过 LangGraph 来研究信息在社交网络中的扩散模式，找出关键的意见领袖节点。
推荐系统 ：构建包含用户、物品等节点以及它们之间交互关系（如购买、浏览等）的图，利用 LangGraph 进行图分析，为用户提供更精准的个性化推荐。例如根据用户和物品在图中的关联路径和相似度等来推荐用户可能感兴趣的新物品。
LangGraph 作为一种新兴的结合了图计算和语言模型等优势的框架，在众多领域都有着广阔的应用前景，随着技术的不断发展，它也将不断完善和拓展其应用场景。""")


async def main():
    await graph.ainvoke({'docs': [doc]}, config=thread_config)


if __name__ == '__main__':
    asyncio.run(main())
