from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, confloat  # 注意新的导入方式
from openai import OpenAI
import re
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_prompt(dialect, ddl_prompt, doc_prompt):
    prompt = f"""
    请作为资深DBA严格评估以下SQL，遵循规则：

    ### 评估规则
    1. **语法检查**：
       - 是否符合{dialect}语法？是否存在保留字未转义？
       - 是否错误使用方言（如MySQL的LIMIT vs. SQL Server的TOP）？
       - 是否有语法错误（如括号不匹配、关键字拼写错误）？
       - 是否有逗号、分号等标点符号使用错误？
       - 是否有不支持的函数或操作符？
       - SQL关键字是否使用了正确的大小写风格？
       - 分页语法是否正确（MySQL的LIMIT vs Oracle的FETCH）？

    2. **意图匹配**：
       - 是否完整覆盖问题需求？检查以下方面：
        - 必检项：
            - 筛选条件（WHERE/HAVING）
            - 聚合与非聚合字段混合使用
            - 结果集是否符合预期（字段数量、类型、含义）
            - 是否处理了需求中的所有特殊情况和边界条件
        - 条件检查项：
            - 排序（ORDER BY）- 仅在需求明确要求时检查
            - 数量限制（LIMIT/TOP）- 仅在需求明确要求时检查
            - 分组（GROUP BY）- 仅在需求明确要求时检查
            - 去重（DISTINCT）- 仅在需求明确要求时检查
       - 注意：如果用户需求中未明确要求使用LIMIT/TOP或ORDER BY，则不应将其缺失视为错误
       - 是否存在过度查询（返回不必要的数据）？

    3. **Schema适配性**：
       - 字段类型是否匹配（如用字符串比较数字字段）？  
       - 表名和列名是否与数据库结构匹配？表/列是否存在？
       - 数据库结构定义  {ddl_prompt} 
       - 是否正确使用了表别名？别名是否一致？
       - 是否存在列名冲突（如多表JOIN时未指定表前缀）？
       - 外键关系是否正确使用？
       - 是否正确处理了数据类型转换？

    4. **逻辑正确性**：
       - NULL处理是否正确（`IS NULL` vs `= NULL`）？
       - JOIN条件是否避免笛卡尔积？
       - 子查询是否可优化为JOIN？
       - 条件逻辑是否正确（AND/OR优先级、括号使用）？
       - 是否存在冗余或矛盾的条件？
       - 聚合函数使用是否正确（如COUNT、SUM、AVG等）？
       - 是否正确处理了重复数据？
       - 日期时间处理是否正确？
       - 数学计算是否正确（除零、溢出风险等）？

    5. **性能与健壮性**：
       - 是否存在全表扫描风险（如未使用索引字段）？
       - 是否使用不安全的通配符（如`SELECT *`）？
       - 是否有不必要的子查询或临时表？
       - 是否有可合并的多次查询？
       - 是否存在过度复杂的JOIN（如超过5个表的JOIN）？
       - 是否存在不必要的排序或分组操作？
       - 是否有效利用了数据库特有的优化特性？
       - 是否存在不必要的类型转换导致的性能问题？

    6. **安全性评估**：
       - 是否存在SQL注入风险？
       - 是否正确处理了用户输入参数？
       - 是否存在权限问题（如访问未授权的表或列）？
       - 是否存在敏感数据泄露风险？

    7. **可维护性**：
       - SQL格式是否清晰易读（缩进、换行、命名规范）？
       - 是否有适当的注释说明复杂逻辑？
       - 是否遵循了命名约定（如表名、列名、别名等）？
       - 是否存在过度复杂的表达式？

    8. **数据一致性**：
       - 是否正确处理了事务（如需要时）？
       - 是否存在可能导致数据不一致的操作？
       - 是否正确处理了外键约束？

    9. **特定数据库优化**：
       - 是否利用了{dialect}特有的优化特性？
       - 是否避免了{dialect}已知的性能陷阱？
       - 是否使用了适合{dialect}的函数和语法？

    ### 需求说明
    {doc_prompt}

    ### 输出要求
    按JSON格式，包含：
    - 总体通过状态与得分（0-1）
    - 错误详细
    - 错误分类标签
    - 可选的SQL优化建议

    严格遵守输出格式：  
    {{  
      "overall": {{"pass": false, "score": 0.4}},  
      "details": {{  
        "syntax": {{"error_messages": ["..."]}},  
        "semantic": {{"missing_conditions": ["..."]}}  
      }},  
      "error_types": ["SCHEMA_MISMATCH"],  
      "suggestions": ["..."]
      }}
    """
    return prompt

# ---------- 嵌套对象定义 ----------
@dataclass
class SyntaxDetails:
    error_messages: List[str]


@dataclass
class SemanticDetails:
    missing_conditions: List[str]
    schema_mismatch: Optional[List[str]] = None

    def __init__(self, missing_conditions: List[str], **kwargs):
        self.missing_conditions = missing_conditions
        self.schema_mismatch = kwargs.get('schema_mismatch', None)


class Details(BaseModel):
    syntax: SyntaxDetails
    semantic: SemanticDetails

    @classmethod
    def parse_details(cls, data: Dict[str, Any]):
        return cls(
            syntax=SyntaxDetails(**data.get('syntax', {'error_messages': []})),
            semantic=SemanticDetails(**data.get('semantic', {'missing_conditions': []}))
        )


class ValidationResult(BaseModel):
    class Overall(BaseModel):
        is_pass: bool = Field(..., alias="pass")
        score: confloat(ge=0, le=1)

    overall: Overall
    details: Details
    error_types: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

    @classmethod
    def from_json(cls, json_str: str):
        import json
        try:
            # 提取JSON字符串
            if isinstance(json_str, str):
                json_str = extract_json(json_str)
                raw_data = json.loads(json_str)
            else:
                raw_data = json_str

            # 构建验证结果对象
            return cls(
                overall=cls.Overall(**raw_data.get('overall', {'pass': False, 'score': 0})),
                details=Details.parse_details(raw_data.get('details', {
                    'syntax': {'error_messages': []},
                    'semantic': {'missing_conditions': []}
                })),
                error_types=raw_data.get('error_types', []),
                suggestions=raw_data.get('suggestions', [])
            )
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            # 返回一个默认对象而不是抛出异常
            return cls(
                overall=cls.Overall(pass_=False, score=0),
                details=Details.parse_details({
                    'syntax': {'error_messages': [str(e)]},
                    'semantic': {'missing_conditions': []}
                }),
                error_types=['PARSE_ERROR'],
                suggestions=['请检查输入格式是否正确']
            )

    def to_dict(self) -> Dict:
        return self.model_dump(by_alias=True)


def extract_json(llm_response: str) -> str:
    if not isinstance(llm_response, str):
        return llm_response

    json_str = re.findall(r"```json\n(.*)```", llm_response, re.DOTALL)
    if json_str:
        return json_str[-1]

    json_str = re.findall(r"```(.*)```", llm_response, re.DOTALL)
    if json_str:
        return json_str[-1]

    return llm_response

def add_ddl_to_prompt( ddl_list: list[str]) -> str:
    if len(ddl_list) > 0:
        prompt = "\n===Tables \n\n"
        for ddl in ddl_list:
            prompt += f"{ddl}\n\n"
        return prompt

def add_documentation_to_prompt(documentation_list: list[str]) -> str:
    if len(documentation_list) > 0:
        prompt = "\n"
        for documentation in documentation_list:
            prompt += f"{documentation}\n\n"
        return prompt

def build_evaluation_prompt(dialect, schema,doc):
    ddl_prompt = add_ddl_to_prompt(schema)
    doc_prompt = add_documentation_to_prompt(doc)
    prompt = get_prompt(dialect, ddl_prompt, doc_prompt)
    return prompt

def build_question_prompt(question,sql, sql_result):
    prompt = f"""
### 问题
 {question}

### sql
{sql}

### sql运行结果
{sql_result}
     """
    return prompt
def get_evalutaion_result(client,model,question,dialect,schema,sql,sql_result):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": build_evaluation_prompt(dialect, schema)},
                  {"role": "user", "content": build_question_prompt(question,sql, sql_result)}],
        stop=None,
        temperature=0.7
    )

    if response.choices[0].message.reasoning_content:
        logger.info(f"评估 思考过程：{response.choices[0].message.reasoning_content}")

    if response.choices[0].message.content:
        logger.info(f"评估 结果：{response.choices[0].message.content}")

    result = ValidationResult.from_json(response.choices[0].message.content)

    logger.info(f"评估 结果-ValidationResult：{str(result)}")

    return result

if __name__ == '__main__':
    json_str = '''
    {
      "overall": {
        "pass": false,
        "score": 0.2
      },
      "details": {
        "syntax": {
          "error_messages": []
        },
        "semantic": {
          "missing_conditions": [],
          "schema_mismatch": ["Table 'teachers' does not exist in gas_management_system"]
        }
      },
      "error_types": ["SCHEMA_MISMATCH"],
      "suggestions": [
        "1. 确认数据库上下文是否正确（当前数据库为gas_management_system）",
        "2. 检查表名拼写是否符合实际schema（可能需要复数形式或不同命名如teacher/staff）",
        "3. 验证数据库权限及连接配置",
        "4. 建议使用SHOW TABLES确认可用表清单"
      ]
    }
    '''

    result = ValidationResult.from_json(json_str)
    print(result.to_dict())