#!/user/bin/env python3
# -*- coding: utf-8 -*-
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langgraph_api.examples.rag.indexing_2 import retriever
from langgraph_api.examples.rag.retrieval_3 import docs

# Prompt
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
print(prompt)

# LLM
llm = ChatOpenAI(model_name="DeepSeek-R1-Distill-Qwen-32B", temperature=0)

# Chain
chain = prompt | llm

# Run
chain.invoke({"context":docs, "question":"What is Task Decomposition?"})

from langchain import hub
prompt_hub_rag = hub.pull("rlm/rag-prompt")

print(prompt_hub_rag)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(rag_chain.invoke("What is Task Decomposition?"))
