import os
from dotenv import load_dotenv

load_dotenv()

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
