import argparse
import os
import threading

from dotenv import load_dotenv
from huggingface_hub import login
from scripts.text_inspector_tool import TextInspectorTool
from scripts.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SearchInformationTool,
    SimpleTextBrowser,
    VisitTool,
)
from scripts.visual_qa import visualizer

from smolagents import (
    CodeAgent,
    # HfApiModel,
    LiteLLMModel,
    ToolCallingAgent, OpenAIServerModel,
)


AUTHORIZED_IMPORTS = [
    "requests",
    "zipfile",
    "os",
    "pandas",
    "numpy",
    "sympy",
    "json",
    "bs4",
    "pubchempy",
    "xml",
    "yahoo_finance",
    "Bio",
    "sklearn",
    "scipy",
    "pydub",
    "io",
    "PIL",
    "chess",
    "PyPDF2",
    "pptx",
    "torch",
    "datetime",
    "fractions",
    "csv",
]
load_dotenv(override=True)
# login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--question", type=str, default='多智能体的框架都有哪些', help="for example: 'How many studio albums did Mercedes Sosa release before 2007?'"
    )
    # parser.add_argument("--model-id", type=str, default="o1")
    return parser.parse_args()


custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": user_agent},
        "timeout": 300,
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY"),
}

os.makedirs(f"./{BROWSER_CONFIG['downloads_folder']}", exist_ok=True)


def main():
    args = parse_args()
    text_limit = 100000

    # model = LiteLLMModel(
    #     args.model_id,
    #     custom_role_conversions=custom_role_conversions,
    #     max_completion_tokens=8192,
    #     reasoning_effort="high",
    # )
    model = OpenAIServerModel(
        model_id="DeepSeek-R1-Distill-Qwen-32B",
        api_base="http://ai-api.e-tudou.com:9000/v1/",  # Leave this blank to query OpenAI servers.
        api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57',
        # Switch to the API key for the server you're targeting.
    )

    document_inspection_tool = TextInspectorTool(model, text_limit)

    browser = SimpleTextBrowser(**BROWSER_CONFIG)

    WEB_TOOLS = [
        SearchInformationTool(browser),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
    ]

    text_webbrowser_agent = ToolCallingAgent(
        model=model,
        tools=WEB_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="search_agent",
        description="""你是团队内擅长搜索互联网来回答问题。
对于所有需要上网查找的问题，都可以向他提问。
请尽可能提供更多的背景信息，特别是如果你需要在特定时间段内搜索的话！
而且不要犹豫，可以给他一些复杂的搜索任务，比如找出两个网页之间的差异。
你的请求必须是一个完整的句子，而不是几个关键词的简单堆砌！比如“帮我找到这些信息（……）”，而不是几个关键词。""",
        provide_run_summary=True,
    )
    text_webbrowser_agent.prompt_templates["managed_agent"]["task"] += """您可以访问在线的.txt文件。
如果非HTML页面是其他格式，特别是.pdf或视频，请使用“inspect_file_as_text”工具来检查它。
此外，如果在搜索后发现需要更多信息来回答问题，您可以使用final_answer（带有您的澄清请求作为参数）来请求更多信息。"""

    # manager_agent = CodeAgent(
    #     model=model,
    #     tools=[visualizer, document_inspection_tool],
    #     max_steps=12,
    #     verbosity_level=2,
    #     additional_authorized_imports=AUTHORIZED_IMPORTS,
    #     planning_interval=4,
    #     managed_agents=[text_webbrowser_agent],
    # )

    manager_agent = ToolCallingAgent(
        model=model,
        tools=[visualizer, document_inspection_tool],
        max_steps=12,
        verbosity_level=2,
        planning_interval=4,
        managed_agents=[text_webbrowser_agent],
    )

    answer = manager_agent.run(args.question)
    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
