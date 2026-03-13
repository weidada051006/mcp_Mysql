import os
from pathlib import Path
from dotenv import load_dotenv

# 从项目根目录加载 .env（backend 的上级目录）
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
