import os
from enum import Enum
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

DEFAULT_REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list of table) that distills the main body sections 
   - Provide a concise summary of the report"""


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    GOOGLE = "google"


class PlannerProvider(Enum):
    OPENAI = "openai"
    GROQ = "groq"


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE # Defaults to the default report structure
    number_of_queries: int = 2 # Number of search queries to generate per iteration
    max_search_depth: int = 2 # Maximum number of reflection + search iterations
    planner_provider: PlannerProvider = PlannerProvider.OPENAI # Defaults to OpenAI as provider
    # planner_model: str = "moonshot-v1-8k" # Defaults to OpenAI o3-mini as planner model
    planner_model: str = "moonshot-v1-128k" # Defaults to OpenAI o3-mini as planner model
    writer_model: str = "AgentOS-Chat-72B" # Defaults to Anthropic as provider
    # model = ChatOpenAI(model="gpt-4o")
    # model = ChatOpenAI(model="AgentOS-Chat-72B")
    # model = ChatOpenAI(model="Qwen2.5-72B-Instruct-AWQ")
    # writer_model: str = "moonshot-v1-8k" # Defaults to Anthropic as provider
    # writer_model: str = "moonshot-v1-8k" # Defaults to Anthropic as provider
    search_api: SearchAPI = SearchAPI.GOOGLE # Default to TAVILY

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})