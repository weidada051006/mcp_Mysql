import sys
import getpass
from config import MYSQL_PASSWORD


def verify_password():
    """提示用户输入密码，并与配置的密码比对，返回是否验证成功"""
    prompt = "请输入数据库密码以执行此操作："
    # Cursor/VS Code 集成终端不是完整 TTY，getpass 无法接收输入，改用 input
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
