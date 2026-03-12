from llm_client import parse_llm_response
from db_connection import init_database
import db_operations as db_ops
from auth import verify_password

# 定义哪些操作需要密码验证
SENSITIVE_OPS = {"add_product", "add_products", "delete_product", "delete_products", "delete_product_by_name", "update_product"}

# 函数名到实际函数的映射
function_map = {
    "add_product": db_ops.add_product,
    "add_products": db_ops.add_products,
    "delete_product": db_ops.delete_product,
    "delete_products": db_ops.delete_products,
    "delete_product_by_name": db_ops.delete_product_by_name,
    "update_product": db_ops.update_product,
    "query_products": db_ops.query_products,
}


def main():
    print("=" * 50)
    print("自然语言数据库查询系统（输入 exit 退出）")
    print("注意：增、删、改操作需要验证数据库密码")
    print("示例：")
    print("  - 添加一个商品叫苹果，价格5.5元，库存100")
    print("  - 依次添加草莓6元188库存、甘蔗8元288库存、芭乐15元22库存")
    print("  - 查询所有商品 / 查找名字包含'苹果'的商品")
    print("  - 价格在2元到8元的商品有几个？")
    print("  - 删除草莓商品 / 删除ID为1的商品 / 批量删除ID 2和3")
    print("  - 将商品ID2的价格改为6.8元")
    print("=" * 50)

    # 确保数据库已初始化
    init_database()

    # 对话历史，用于 LLM 上下文理解（仅保留 user / assistant 文本摘要）
    conversation = []

    while True:
        user_input = input("\n请输入您的指令：").strip()
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break
        if not user_input:
            continue

        # 将本轮用户输入加入历史后调用 LLM（带完整上下文）
        conversation.append({"role": "user", "content": user_input})
        calls_list, text_content = parse_llm_response(conversation)

        if calls_list is None:
            # LLM 未调用工具，输出文本回复
            print("\n" + "=" * 50)
            print("AI回复：")
            print(text_content)
            print("=" * 50)
            conversation.append({"role": "assistant", "content": text_content})
        else:
            need_password = any(fn in SENSITIVE_OPS for fn, _ in calls_list)
            if need_password and not verify_password():
                conversation.pop()  # 本轮未执行，去掉刚加的用户消息
                continue
            results = []
            for func_name, args in calls_list:
                print(f"识别到操作：{func_name}，参数：{args}")
                if func_name in function_map:
                    try:
                        result = function_map[func_name](**args)
                        results.append(result)
                    except Exception as e:
                        results.append(f"执行 {func_name} 出错：{str(e)}")
                else:
                    results.append(f"错误：未知函数 {func_name}")
            print("\n" + "=" * 50)
            print("操作结果：")
            for r in results:
                print(r)
            print("=" * 50)
            # 将本轮执行结果摘要加入历史，便于下一轮上下文理解（如「删除它」）
            summary = "；".join(results)
            conversation.append({"role": "assistant", "content": f"已执行：{summary}"})


if __name__ == "__main__":
    main()
