from langfuse import Langfuse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

langfuse = Langfuse(
            secret_key="sk-lf-da22769f-4a7e-4b1e-825a-5fe6cd7fe5d3",
            public_key="pk-lf-311af533-947b-40ef-a70a-d415430e40ad",
            host="http://10.1.3.122:3005"
)

sql_prompt = langfuse.get_prompt("summary-prompt")

sql_prompt = sql_prompt.compile(
    text="文章内容...",
    requirements="限制在 200 字以内"
)

print(sql_prompt)

