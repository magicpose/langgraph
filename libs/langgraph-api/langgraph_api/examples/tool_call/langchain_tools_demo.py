import asyncio
import json

from langchain_core.tools import Tool
from sdk import SkillRequest, SkillExecutorParam, glo

glo.set_skill_base_host('http://apisix-dev1.e-tudou.com:9080/aosk')
glo.set_assistant_base_host("http://10.0.36.113:9080/asst")


class DownloadsTool(Tool):
    name = "model_download_counter"
    description = """
    This is a tool that returns the most downloaded model of a given task.
    It returns the name of the checkpoint."""
    inputs = {
        "task": {
            "type": "string",
            "description": "the task category (such as text-classification, depth-estimation, etc)",
        }
    }
    output_type = "string"

    def forward(self, task: str):
        # todo 调用技能中心或tool本身
        skill_id = ""
        headers = {
            "satoken": "33b4ce4f-c46c-4340-a333-0c8439556ce7",
            "bizToken": "xaaaasadadasdadadadad"  # 生成方法见下
        }
        path = {}  # rest参数
        params = {}  # query参数
        body = {}  # 请求体参数
        param = SkillExecutorParam(skill_id=skill_id, header=headers, path=path, params=params, body=body)

        message = json.dumps(param.to_json())
        sdk = SkillRequest()

        async def event_stream():
            queue = asyncio.Queue()

            async def queue_callback(msg):
                print(f"Received message: {msg}")
                #  回调中处理msg
                await queue.put(msg)

            sdk = SkillRequest()
            param = SkillExecutorParam(skill_id='1863428183523663872', header={
                "satoken": "39e39d0f-3351-40a5-b59a-3d30aec85315",
                "bizToken": "eJyrVkpMT80r8UxRslJQMlTSUVAqTi0uzszPQxbJzszJQeLnAlUAdSGJlKTmJaIYUlqcWgTj1gIAh5YbVQ=="
            }, path={"id": "1802904247175053312"})

            message = json.dumps(param.to_json())
            print(message)
            await sdk.execute_request(message, callback=queue_callback)

            while True:
                msg = await queue.get()
                if msg == 'TERMINATE':
                    break

                print(f"Send message: {msg}")
                # 输出msg
                yield f"data:{msg}\n\n"

        def sync_function():
            # 获取当前事件循环
            loop = asyncio.get_event_loop()
            try:
                # 运行异步方法
                result = loop.run_until_complete(event_stream())
                print("Async result:", result)
            finally:
                # 关闭事件循环（Python 3.10+ 中，可以使用 loop.close()）
                loop.close()

        sync_function()

        # return 'model.id'
