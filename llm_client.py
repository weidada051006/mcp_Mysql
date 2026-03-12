from openai import OpenAI
from config import SILICONFLOW_API_KEY
from tools import tools
import json

client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

# 系统提示：明确删除 vs 查询意图，避免将「删除」误判为「查询」
SYSTEM_PROMPT = """你是商品数据库操作助手，必须根据用户意图选择正确工具：

1. **删除/移除/去掉**：用户说「删除xxx」「去掉xxx商品」「移除草莓」等时，必须调用删除类工具，绝不能调用 query_products。
   - 用户只说商品名称（如「删除草莓」）→ 使用 delete_product_by_name(name="草莓")。
   - 用户明确给出ID（如「删除ID为5的商品」）→ 使用 delete_product(product_id=5)。

2. **查看/查询/列出/显示**：用户说「查看」「查询」「列出」「有多少」「几个」等且没有删除意图时，使用 query_products，可带 condition、price_min/max、stock_min/max、return_count_only 等参数。

3. **结合上下文**：根据对话历史理解指代（如「删除它」「把刚才那个删掉」指代上一条提到的商品），并选用对应工具与参数。"""

# 对话历史保留最近几轮，避免上下文过长（约 10 轮 = 20 条消息）
MAX_HISTORY_MESSAGES = 20


def parse_llm_response(messages):
    """根据完整对话历史调用 LLM，解析所有 function call。
    messages: 列表 [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}, ...]，不含 system。
    返回 (calls_list, None) 或 (None, content)；calls_list 为 [(func_name, args_dict), ...]。"""
    try:
        # 构造完整消息：system + 最近历史 + 确保最后一条是 user
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
        return None, f"LLM调用失败：{str(e)}"
