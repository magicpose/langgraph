import re
from typing import Annotated, Iterator, Literal, TypedDict

from langchain import hub
from langchain_community.document_loaders import web_base
from langchain_community.vectorstores import Chroma
# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, AIMessage, convert_to_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.retrievers import BaseRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, add_messages
from langgraph_api.examples.base_tools import GoogleSerperSearchTool

MAX_RETRIES = 3

# Index 3 pages from Pandas user guides
SOURCE_URLS = [
    'https://pandas.pydata.org/docs/user_guide/indexing.html',
    'https://pandas.pydata.org/docs/user_guide/groupby.html',
    'https://pandas.pydata.org/docs/user_guide/merging.html'
]

NEWLINE_RE = re.compile("\n+")


class PandasDocsLoader(web_base.WebBaseLoader):
    def lazy_load(self) -> Iterator[Document]:
        """Lazy load text from the url(s) in web_path."""
        for path in self.web_paths:
            soup = self._scrape(path, bs_kwargs=self.bs_kwargs)
            text = soup.get_text(**self.bs_get_text_kwargs)
            text = NEWLINE_RE.sub("\n", text)     
            metadata = web_base._build_metadata(soup, path)
            yield Document(page_content=text, metadata=metadata)


def prepare_documents(urls: list[str]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            r"In \[[0-9]+\]",
            r"\n+",
            r"\s+"
        ],
        is_separator_regex=True,
        chunk_size=1000
    )
    docs = [PandasDocsLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]
    return text_splitter.split_documents(docs_list)


def get_retriever() -> BaseRetriever:
    documents = prepare_documents(SOURCE_URLS)
    vectorstore = Chroma.from_documents(
        documents=documents,
        collection_name="pandas-rag-chroma",
        embedding=OpenAIEmbeddings(),
    )
    retriever = vectorstore.as_retriever()
    return retriever


# LLM / Retriever / Tools
# llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
# llm = ChatOpenAI(model="claude-3-5-sonnet-20240620", temperature=0)
llm = ChatOpenAI(model="DeepSeek-R1-Distill-Qwen-32B", temperature=0)
retriever = get_retriever()
# tavily_search_tool = TavilySearchResults(max_results=3)
google_search_tool = GoogleSerperSearchTool()

# Prompts / data models

RAG_PROMPT: ChatPromptTemplate = hub.pull("rlm/rag-prompt")


class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


HALLUCINATION_GRADER_SYSTEM = (
"""
You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts.
Give a binary score 'yes' or 'no', where 'yes' means that the answer is grounded in / supported by the set of facts.

IF the generation includes code examples, make sure those examples are FULLY present in the set of facts, otherwise always return score 'no'.
"""
)
HALLUCINATION_GRADER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", HALLUCINATION_GRADER_SYSTEM),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)


class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


ANSWER_GRADER_SYSTEM = (
"""
You are a grader assessing whether an answer addresses / resolves a question.
Give a binary score 'yes' or 'no', where 'yes' means that the answer resolves the question.
"""
)
ANSWER_GRADER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", ANSWER_GRADER_SYSTEM),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)


QUERY_REWRITER_SYSTEM = (
"""
You a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval.
Look at the input and try to reason about the underlying semantic intent / meaning.
"""
)
QUERY_REWRITER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", QUERY_REWRITER_SYSTEM),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)


class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    question: str
    documents: list[Document]
    candidate_answer: str
    retries: int
    web_fallback: bool


class GraphConfig(TypedDict):
    max_retries: int


def document_search(state: GraphState):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = convert_to_messages(state["messages"])[-1].content

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question, "web_fallback": True}


def generate(state: GraphState):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    retries = state["retries"] if state.get("retries") is not None else -1

    rag_chain = RAG_PROMPT | llm | StrOutputParser()
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"retries": retries + 1, "candidate_answer": generation}


def transform_query(state: GraphState):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """
    print("---TRANSFORM QUERY---")
    question = state["question"]

    # Re-write question
    query_rewriter = QUERY_REWRITER_PROMPT | llm | StrOutputParser()
    better_question = query_rewriter.invoke({"question": question})
    return {"question": better_question}


def web_search(state: GraphState):
    print("---RUNNING WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]
    search_results = google_search_tool.forward(question)
    search_content = "\n".join([d["snippet"] for d in search_results])
    documents.append(Document(page_content=search_content, metadata={"source": "websearch"}))
    return {"documents": documents, "web_fallback": False}


### Edges


def grade_generation_v_documents_and_question(state: GraphState, config) -> Literal["generate", "transform_query", "web_search", "finalize_response"]:
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """
    question = state["question"]
    documents = state["documents"]
    generation = state["candidate_answer"]
    web_fallback = state["web_fallback"]
    retries = state["retries"] if state.get("retries") is not None else -1
    max_retries = config.get("configurable", {}).get("max_retries", MAX_RETRIES)

    # this means we've already gone through web fallback and can return to the user
    if not web_fallback:
        return "finalize_response"

    print("---CHECK HALLUCINATIONS---")
    hallucination_grader = HALLUCINATION_GRADER_PROMPT | llm.with_structured_output(GradeHallucinations)
    hallucination_grade: GradeHallucinations = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    # Check hallucination
    if hallucination_grade.binary_score == "no":
        return "generate" if retries < max_retries else "web_search"

    print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")

    # Check question-answering
    print("---GRADE GENERATION vs QUESTION---")

    answer_grader = ANSWER_GRADER_PROMPT | llm.with_structured_output(GradeAnswer)
    answer_grade: GradeAnswer = answer_grader.invoke({"question": question, "generation": generation})
    if answer_grade.binary_score == "yes":
        print("---DECISION: GENERATION ADDRESSES QUESTION---")
        return "finalize_response"
    else:
        print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
        return "transform_query" if retries < max_retries else "web_search"


def finalize_response(state: GraphState):
    print("---FINALIZING THE RESPONSE---")
    return {"messages": [AIMessage(content=state["candidate_answer"])]}


# Define graph

workflow = StateGraph(GraphState, config_schema=GraphConfig)

# Define the nodes
workflow.add_node("document_search", document_search)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)
workflow.add_node("web_search", web_search)
workflow.add_node("finalize_response", finalize_response)

# Build graph
workflow.set_entry_point("document_search")
workflow.add_edge("document_search", "generate")
workflow.add_edge("transform_query", "document_search")
workflow.add_edge("web_search", "generate")
workflow.add_edge("finalize_response", END)

workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question
)

from langfuse import Langfuse

langfuse = Langfuse(
  secret_key="sk-lf-45977ced-899f-41a4-bd99-2aa48b5f6988",
  public_key="pk-lf-a8db51d2-7534-4218-98bc-7af2d9651e04",
  host="http://10.1.3.122:3005"
)

from langfuse.callback import CallbackHandler

# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler(
    secret_key="sk-lf-45977ced-899f-41a4-bd99-2aa48b5f6988",
    public_key="pk-lf-a8db51d2-7534-4218-98bc-7af2d9651e04",
    host="http://10.1.3.122:3005"
)

memory = MemorySaver()

# thread_config = {"configurable": {"thread_id": "123"}, 'callbacks': [langfuse_handler]}

# Compile
graph = workflow.compile(checkpointer=memory)

# graph.get_graph().draw_mermaid_png(output_file_path='pandas.png')
# graph.invoke({'messages': [{'role': 'ai', 'content': '我是智能问答助手'}], 'question': 'pandas是什么？'}, config=thread_config)
