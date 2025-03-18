from typing import Annotated, List, TypedDict, Literal
from pydantic import BaseModel, Field
import operator


class Section(BaseModel):
    name: str = Field(
        description="报告这一部分的名称.",
    )
    description: str = Field(
        description="本部分的主题和简要概述.",
    )
    research: bool = Field(
        description="是否为报告的这一部分进行网络研究."
    )
    content: str = Field(
        description="这一部分的内容."
    )   


class Sections(BaseModel):
    sections: List[Section] = Field(
        description="报告的部分.",
    )


class SearchQuery(BaseModel):
    search_query: str = Field(None, description="网络搜索查询.")


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="搜索查询列表.",
    )


class Feedback(BaseModel):
    grade: Literal["pass","fail"] = Field(
        description="评估结果，表明回答是否符合要求（'pass'）或需要修改（'fail'）."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="后续搜索查询列表.",
    )


class ReportStateInput(TypedDict):
    topic: str # Report topic


class ReportStateOutput(TypedDict):
    final_report: str # Final report


class ReportState(TypedDict):
    topic: str # Report topic    
    sections: list[Section] # List of report sections 
    completed_sections: Annotated[list, operator.add] # Send() API key
    report_sections_from_research: str # String of any completed sections from research to write final sections
    final_report: str # Final report


class SectionState(TypedDict):
    section: Section # Report section  
    search_iterations: int # Number of search iterations done
    search_queries: list[SearchQuery] # List of search queries
    source_str: str # String of formatted source content from web search
    feedback_on_report_plan: str # Feedback on the report plan
    report_sections_from_research: str # String of any completed sections from research to write final sections
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API


class SectionOutputState(TypedDict):
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API
