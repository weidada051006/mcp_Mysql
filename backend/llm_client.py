import json
from openai import OpenAI

from .config import SILICONFLOW_API_KEY
from .tools import tools

client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

SYSTEM_PROMPT = """你是自然语言理解与数据库操作助手。**所有用户输入都必须由你处理并回复**，不得忽略任何一条消息。

**处理规则：**
1. **仅当用户意图涉及「商品数据库」的增、删、改、查时**，才调用工具（add_product、delete_product、query_products 等），并严格按用户条件传参（如「库存大于100」必须传 stock_min=101）。
2. **其他所有情况**（打招呼、闲聊、与数据库无关的问题、无法理解的内容等），请直接用自然语言简短友好回复，不要调用任何工具。例如：你好、谢谢、今天天气不错、随便问问 等，都只回复文字。

**涉及数据库时的工具选择：**
- 删除/移除某商品 → delete_product_by_name 或 delete_product。
- 查看/查询/列出/有多少/几个 → query_products，注意「库存大于N」传 stock_min=N+1，「价格A到B」传 price_min、price_max。
- 添加/更新商品 → add_product、add_products、update_product。

**结合对话上下文**理解指代（如「删除它」「再查一次」）。"""

MAX_HISTORY_MESSAGES = 20


def parse_llm_response(messages):
    """根据完整对话历史调用 LLM，解析所有 function call。
    messages: 列表 [{"role":"user","content":"..."}, ...]，不含 system。
    返回 (calls_list, None) 或 (None, content)。"""
    try:
        full = [{"role": "system", "content": SYSTEM_PROMPT}]
        if messages:
            full.extend(messages[-MAX_HISTORY_MESSAGES:])
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-32b-instruct",
            messages=full,
            tools=tools,
            tool_choice="auto"
        )
        message = response.choices[0].message
        if message.tool_calls:
            calls_list = []
            for tc in message.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                calls_list.append((name, args))
            return calls_list, None
        return None, message.content or ""
    except Exception as e:
        err = str(e).strip().lower()
        if "connection" in err or "timeout" in err or "network" in err:
            return None, "网络或服务暂时不可用，请检查网络后稍后重试。"
        return None, f"服务暂时异常，请稍后重试。（{str(e)[:80]}）"
