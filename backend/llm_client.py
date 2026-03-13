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
- 数据格式只有「名称、价格、库存」，没有 ID。前几条/后几条一律按**入库顺序**（先进入数据库的在前）。
- 删除：按名称删用 delete_product_by_name；按 ID 删用 delete_product/delete_products。**「删除前三个」「去掉前N条」用 delete_first_n_products(n)；「删除后三个」「最后N条」用 delete_last_n_products(n)**。
- 查看/查询/列出 → query_products。「前三个」「前5条」传 limit=3、limit=5；「后三个」「最后5条」传 last_n=3、last_n=5。
- 添加/更新 → add_product、add_products、update_product。

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
