from typing import Dict, TypedDict, Annotated, Sequence, Optional
from typing import Literal
from langchain_core.callbacks import BaseCallbackHandler
from tqdm import tqdm
from dataclasses import dataclass, field

import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DetailedCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.step_count = 0

    def on_chain_start(self, serialized: Optional[dict] = None, inputs: Optional[dict] = None, **kwargs):
        self.step_count += 1
    #     node_name = serialized.get('name', 'unknown') if serialized else 'unknown'
    #     print(f"[Step{self.step_count}] 🚀 开始执行: {node_name}")
    #
    #     # if inputs and 'messages' in inputs:
    #     #     messages = inputs['messages']
    #     # if messages and len(messages) > 0:
    #     #     print(f"最新消息: {messages[-1].content}")
    #
    # def on_chain_end(self, outputs: Optional[dict] = None, **kwargs):
    #     if outputs and 'messages' in outputs:
    #         messages = outputs['messages']
    #         if messages and len(messages) > 0:
    #             print(f"节点输出: {messages[-1].content}")
    #     print(f"[Step {self.step_count}] ✅ 执行完成")

    # def on_llm_start(self, *args, **kwargs):
    #     print("📝 LLM 开始生成...")
    #
    # def on_llm_end(self, *args, **kwargs):
    #     print("✨ LLM 生成完成")
    #
    # def on_chain_error(self, error: Exception, **kwargs):
    #     print(f"❌ 错误发生: {str(error)}")