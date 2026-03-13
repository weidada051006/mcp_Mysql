from .config import MYSQL_PASSWORD


def verify_password(input_password: str) -> bool:
    """验证输入的密码是否与配置密码一致"""
    return input_password == MYSQL_PASSWORD
