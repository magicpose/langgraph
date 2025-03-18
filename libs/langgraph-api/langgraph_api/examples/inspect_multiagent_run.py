# from openinference.instrumentation.smolagents import SmolagentsInstrumentor
# from phoenix.otel import register

from langgraph_api.examples.base_tools import GoogleSerperSearchTool

# register()
# SmolagentsInstrumentor().instrument(skip_dep_check=True)


from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    VisitWebpageTool,
    OpenAIServerModel,
)


# Then we run the agentic part!
model = OpenAIServerModel(
    model_id="DeepSeek-R1-Distill-Qwen-32B",
    api_base="http://ai-api.e-tudou.com:9000/v1/",  # Leave this blank to query OpenAI servers.
    api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57',  # Switch to the API key for the server you're targeting.
)

search_agent = ToolCallingAgent(
    tools=[GoogleSerperSearchTool(), VisitWebpageTool()],
    model=model,
    name="search_agent",
    description="This is an agent that can do web search.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent],
)
manager_agent.run("If the US keeps it 2024 growth rate, how many years would it take for the GDP to double?")
