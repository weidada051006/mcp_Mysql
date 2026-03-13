"""命令行入口：自然语言数据库问答（需验证密码的操作用 getpass 输入密码）
运行方式（在项目根目录）：python -m backend.cli
"""
import getpass

from .llm_client import parse_llm_response
from .models import init_database
from . import db_orm as db_ops
from .auth import verify_password

SENSITIVE_OPS = {"add_product", "add_products", "delete_product", "delete_products", "delete_product_by_name", "update_product"}

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

    init_database()
    conversation = []

    while True:
        user_input = input("\n请输入您的指令：").strip()
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})
        calls_list, text_content = parse_llm_response(conversation)

        if calls_list is None:
            print("\n" + "=" * 50)
            print("AI回复：")
            print(text_content)
            print("=" * 50)
            conversation.append({"role": "assistant", "content": text_content})
        else:
            need_password = any(fn in SENSITIVE_OPS for fn, _ in calls_list)
            if need_password:
                pwd = getpass.getpass("请输入数据库密码以执行此操作：")
                if not verify_password(pwd):
                    print("密码错误，操作取消。")
                    conversation.pop()
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
            summary = "；".join(results)
            conversation.append({"role": "assistant", "content": f"已执行：{summary}"})


if __name__ == "__main__":
    main()
