# 自然语言数据库问答系统（NLP2MySQL）

前后端分离：Vue 前端 + FastAPI 后端 + SQLAlchemy ORM + MySQL。

## 项目结构

```
nlp2mysql/
├── .env                 # 环境变量（MYSQL_PASSWORD、SILICONFLOW_API_KEY），勿提交
├── requirements.txt     # Python 依赖
├── backend/              # 后端（FastAPI + ORM）
│   ├── __init__.py
│   ├── config.py        # 配置（从根目录 .env 加载）
│   ├── models.py        # SQLAlchemy 模型与 init_database
│   ├── db_orm.py        # 数据库操作（ORM）
│   ├── auth.py          # 密码验证
│   ├── tools.py         # LLM 工具定义
│   ├── llm_client.py    # LLM 调用
│   ├── main.py          # FastAPI 应用入口
│   ├── cli.py           # 命令行交互入口
│   └── check_db.py      # 数据库连接与数据检查
└── frontend/            # 前端（Vue + Vite）
    ├── src/
    │   ├── api/         # 请求 /api/parse、/api/execute
    │   ├── components/
    │   └── stores/
    └── ...
```

## 环境准备

1. 在项目根目录创建并激活虚拟环境，安装依赖：
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. 在根目录创建 `.env`，填写：
   - `MYSQL_PASSWORD=你的MySQL root密码`
   - `SILICONFLOW_API_KEY=你的硅基流动 API Key`
3. 确保 MySQL 已安装并启动，且 root 可连接。

## 如何运行

**重要：** 使用前端页面前必须先启动后端，否则会出现「打不开 http://localhost:8000/docs」或前端「请求超时」。前端会检测后端是否可用，若未连接会显示黄色提示条。

- **后端 API**（在项目根目录、先执行并保持运行）：
  ```bash
  venv\Scripts\activate
  uvicorn backend.main:app --reload --port 8000
  ```
  启动成功后，浏览器访问 **http://localhost:8000/docs** 或 **http://127.0.0.1:8000/docs** 可打开 API 文档。
- **命令行版**（在项目根目录执行）：
  ```bash
  python -m backend.cli
  ```
- **前端**（在项目根目录执行，需先启动后端）：
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
  前端默认 `http://localhost:5173`，会通过 Vite 代理将 `/api` 转发到 `http://127.0.0.1:8000`。

## 如何测试

### 1. 检查数据库与后端

在项目根目录、已激活 venv 的前提下：

```bash
# 检查 MySQL 是否可连、products 表是否有数据
python -m backend.check_db
```

若提示连接失败，请检查 MySQL 服务与 `.env` 中的 `MYSQL_PASSWORD`。

### 2. 测试后端 API

在项目根目录执行（保持该终端运行）：

```bash
venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

看到 `Uvicorn running on http://127.0.0.1:8000` 后，再在浏览器打开 **http://localhost:8000/docs** 或 **http://127.0.0.1:8000/docs**，用 Swagger 测试：
  - `POST /api/parse`：body 填 `{"message": "查询所有商品", "history": []}`，应返回 `status: "direct_result"` 及查询结果。
  - 若发「添加商品xxx」会返回 `status: "need_password"` 和 `session_id`，再用 `POST /api/execute` 传该 `session_id` 和 `.env` 中的密码，应返回 `status: "success"`。
- 或访问 **http://localhost:8000/api/health**，应返回 `{"status":"ok"}`。

### 3. 测试命令行版

新开一个终端，在项目根目录：

```bash
venv\Scripts\activate
python -m backend.cli
```

输入「查询所有商品」应直接出结果；输入「添加一个商品草莓 6 元 100 库存」会提示输入数据库密码，正确密码后应添加成功。

### 4. 前后端联调

1. **先**在项目根目录启动后端（保持运行）：`uvicorn backend.main:app --reload --port 8000`
2. **再**新开终端启动前端：`cd frontend` → `npm run dev`
3. 浏览器打开 **http://localhost:5173**。若顶部出现黄色提示「无法连接后端服务」，说明后端未启动或未在 8000 端口运行，请先完成步骤 1 后点击「重试」。
4. 在聊天框输入自然语言（如「有多少个商品」「添加商品西瓜 3 元 50 库存」），确认返回与密码弹窗行为符合预期。若出现「请求超时」，多为后端未启动或 LLM 响应较慢，可先访问 http://localhost:8000/api/health 确认后端是否正常。
