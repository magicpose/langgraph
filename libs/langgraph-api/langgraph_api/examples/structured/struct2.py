#!/user/bin/env python3
# -*- coding: utf-8 -*-
# response_format value as json_schema
from pprint import pprint

from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph_api.examples.structured.struct1 import get_weather, WeatherResponse

# model = ChatOpenAI(model="gpt-4o-mini")
# model = ChatOpenAI(model="gpt-4o")
# model = ChatOpenAI(model="AgentOS-Chat-72B")
# model = ChatOpenAI(model="Qwen2.5-72B-Instruct-AWQ")
# 上面的可以
# model = ChatOpenAI(model="luoshufunctioncall_v3")
# model = ChatOpenAI(model="luoshu_mllm")
model = ChatOpenAI(model="AgentOS-Chat-72B")
# model = ChatOpenAI(model="DeepSeek-R1-Distill-Qwen-32B")
# model = ChatOpenAI(model="moonshot-v1-32k")
# model = ChatOpenAI(model="deepseek-ai/DeepSeek-V3")
# model = ChatOpenAI(model="moonshot-v1-8k")
# model = ChatOpenAI(model="moonshot-v1-128k")


model_with_tools = model.bind_tools([get_weather])
model_with_structured_output = model.with_structured_output(WeatherResponse)


# Define the function that calls the model
def call_model(state: AgentState):
    response = model_with_tools.invoke(state['messages'])
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function that responds to the user
def respond(state: AgentState):
    # We call the model with structured output in order to return the same format to the user every time
    # state['messages'][-2] is the last ToolMessage in the convo, which we convert to a HumanMessage for the model to use
    # We could also pass the entire chat history, but this saves tokens since all we care to structure is the output of the tool
    response = model_with_structured_output.invoke([HumanMessage(content=state['messages'][-2].content)])
    # We return the final answer
    return {"final_response": response}


# Define the function that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we respond to the user
    if not last_message.tool_calls:
        return "respond"
    # Otherwise if there is, we continue
    else:
        return "continue"


tools = [get_weather]

# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("respond", respond)
workflow.add_node("tools", ToolNode(tools))

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "respond": "respond",
    },
)

workflow.add_edge("tools", "agent")
workflow.add_edge("respond", END)
graph = workflow.compile()

# graph.get_graph().draw_mermaid_png(output_file_path='two_llm.png')

if __name__ == '__main__':
    pprint(graph.invoke(input={"messages": [("human", "what's the weather in SF?")]}))
