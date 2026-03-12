import sys
import getpass
from config import MYSQL_PASSWORD


def verify_password():
    """提示用户输入密码，并与配置的密码比对，返回是否验证成功（供命令行使用）"""
    prompt = "请输入数据库密码以执行此操作："
    if sys.stdin.isatty():
        user_input = getpass.getpass(prompt)
    else:
        print("（当前环境无法隐藏输入，密码将明文显示，请留意周围环境）")
        user_input = input(prompt)
    if user_input == MYSQL_PASSWORD:
        return True
    else:
        print("密码错误，操作取消。")
        return False


def verify_password_input(input_password: str) -> bool:
    """接收密码字符串并比对，返回是否验证成功。供 Web API 等非交互场景使用。"""
    if input_password is None:
        return False
    return input_password.strip() == (MYSQL_PASSWORD or "")
