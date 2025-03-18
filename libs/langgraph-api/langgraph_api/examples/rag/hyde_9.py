#!/user/bin/env python3
# -*- coding: utf-8 -*-
from langchain.prompts import ChatPromptTemplate

from langgraph_api.examples.rag.multi_query_5 import retriever

# HyDE document genration
template = """Please write a scientific paper passage to answer the question
Question: {question}
Passage:"""
prompt_hyde = ChatPromptTemplate.from_template(template)

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model='DeepSeek-R1-Distill-Qwen-32B', temperature=0)

generate_docs_for_retrieval = (
    prompt_hyde | llm | StrOutputParser()
)

# Run
question = "What is task decomposition for LLM agents?"
generate_docs_for_retrieval.invoke({"question": question})

# Retrieve
retrieval_chain = generate_docs_for_retrieval | retriever
retireved_docs = retrieval_chain.invoke({"question": question})
print(retireved_docs)

# RAG
template = """Answer the following question based on this context:

{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

final_rag_chain = (
    prompt
    | llm
    | StrOutputParser()
)

print(final_rag_chain.invoke({"context": retireved_docs, "question": question}))
