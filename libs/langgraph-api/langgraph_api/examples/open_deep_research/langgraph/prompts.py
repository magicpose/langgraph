# Prompt to generate search queries to help with planning the report
report_planner_query_writer_instructions="""你是一位专业的技术作家，正在帮助规划一份报告。. 

<Report topic>
{topic}
</Report topic>

<Report organization>
{report_organization}
</Report organization>

<Task>
你的目标是生成{number_of_queries}个搜索查询，以帮助收集用于规划报告各部分的全面信息。
这些查询应该：
1 与报告主题相关。
2 能够满足报告结构中指定的要求。
查询内容应足够具体，以便找到高质量且相关的资料，同时覆盖报告所需的广度。
</Task>"""

# Prompt to generate the report plan
report_planner_instructions="""我想要一个报告的计划. 

<Task>
生成报告各部分的列表。
每个部分应包含以下字段：
名称：该部分的名称。
描述：对该部分涵盖的主要主题的简要概述。
是否进行网络研究：是否需要为该部分进行网络研究。
内容：该部分的内容，目前保留空白。
例如，引言和结论部分不需要进行研究，因为它们将从报告的其他部分提炼信息。
</Task>

<Topic>
报告的主题是：
{topic}
</Topic>

<Report organization>
报告应遵循以下结构：
{report_organization}
</Report organization>

<Context>
以下是用于规划报告各部分的背景信息：
{context}
</Context>

<Feedback>
以下是关于报告结构的评审反馈（如有）：
{feedback}
</Feedback>
"""

# Query writer instructions
query_writer_instructions="""您是一位专业的技术作家，擅长撰写针对性的网络搜索查询语句，以便为撰写技术报告的某个部分收集全面的信息。

<Section topic>
{section_topic}
</Section topic>

<Task>
在生成{number_of_queries}条搜索查询时，请确保它们：
1. 涵盖主题的不同方面（例如，核心功能、实际应用、技术架构）；
2. 包含与主题相关的特定技术术语；
3. 通过添加年份标记（例如“2024”）来定位最近的信息；
4. 寻找与类似技术/方法的比较或差异化内容；
5. 搜索官方文档和实际实现示例。
查询内容应：
- 具体到足以避免泛泛的结果；
- 技术性强到能够捕捉详细的实现信息；
- 多样化到足以覆盖所有方面的计划；
- 专注于权威来源（文档、技术博客、学术论文）。
</Task>"""

# Section writer instructions
section_writer_instructions = """您是一位专业的技术作家，正在撰写一份技术报告的一个部分.

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Source material>
{context}
</Source material>

<Guidelines for writing>
1. 如果现有章节内容为空白，请从头开始撰写一个新章节。
2. 如果现有章节内容已存在，请撰写一个新章节，将现有章节内容与新信息进行整合。
</Guidelines for writing>

<Length and style>
- 严格限制在150-200字以内
- 不使用营销语言
- 以技术为重点
- 使用简单、清晰的语言
- 以最重要的观点开头，并用粗体突出显示
- 使用短段落（最多2-3句）
- 使用##作为部分标题（Markdown格式）
- 如果有助于阐明观点，只使用一个结构元素：
  * 要么是一个集中比较2-3个关键项目的表格（使用Markdown表格语法）
  * 要么是一个简短的列表（3-5个项目），使用正确的Markdown列表语法：
    - 使用*或-表示无序列表
    - 使用1.表示有序列表
    - 确保适当的缩进和间距
- 以 ### Sources结尾，引用以下来源材料，并按以下格式格式化：
  * 按标题、日期和网址列出每个来源
  * 格式：- 标题 : 网址
</Length and style>

<Quality checks>
- 准确控制在150-200字（不包括标题和引用来源）
- 谨慎使用仅一个结构元素（表格或列表），并且只有在有助于阐明观点时才使用
- 提供一个具体示例或案例研究
- 以加粗的洞见开头
- 直接进入内容，不使用前言或引言
- 在文末引用来源
</Quality checks>
"""

# Instructions for section grading
section_grader_instructions = """审查与指定主题相关的报告部分:

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
通过检查技术准确性和深度，评估该部分是否充分覆盖了主题。

如果该部分未能满足任何标准，生成具体的后续搜索查询，以收集缺失的信息。
</task>

<format>
    grade: Literal["pass","fail"] = Field(
        description="评估结果表明该回答是否符合要求（'pass'）或需要修订（'fail'）."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="后续搜索查询列表.",
    )
</format>
"""

final_section_writer_instructions="""您是一位专业的技术撰稿人，正在撰写一个部分，以综合报告中其他部分的信息。

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. 部分特定方法：
对于引言：
- 使用#标注报告标题（Markdown格式）。
- 字数限制为50-100字。
- 使用简单明了的语言。
- 在1-2段中聚焦报告的核心动机。
- 使用清晰的叙事结构来引入报告。
- 不包含结构化元素（无列表或表格）。
- 不需要来源部分。
对于结论/总结：
- 使用##标注章节标题（Markdown格式）。
- 字数限制为100-150字。
- 对于比较性报告：
 * 必须包含一个使用Markdown表格语法的聚焦比较表。
 * 表格应提炼报告中的见解。
 * 保持表格条目清晰简洁。
对于非比较性报告：
 * 如果有助于提炼报告中的要点，仅使用一个结构化元素：
 * 使用Markdown表格语法的聚焦表格比较报告中的项目。
 * 或者使用正确的Markdown列表语法的简短列表：
  - 使用*或-表示无序列表。
  - 使用1.表示有序列表。
  - 确保适当的缩进和间距。
- 以具体的下一步行动或影响结束。
- 不需要来源部分。

3. 写作方法：
- 使用具体细节而非一般性陈述。
- 每个词都要有意义。
- 聚焦于最重要的单一要点。
</Task>

<Quality Checks>
- 对于引言：限制在50-100字以内，使用#标注报告标题，不包含结构化元素，不设来源部分。
- 对于结论：限制在100-150字以内，使用##标注章节标题，最多仅使用一个结构化元素，不设来源部分。
- 使用Markdown格式。
- 回答中不包含字数统计或任何前言。
</Quality Checks>"""