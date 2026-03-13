"""
FastAPI 后端：自然语言数据库问答 API
运行方式（在项目根目录）：uvicorn backend.main:app --reload --port 8000
"""
import uuid
from typing import Optional, Dict, List, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .llm_client import parse_llm_response
from . import db_orm as db_ops
from .auth import verify_password
from .models import init_database

app = FastAPI(title="自然语言数据库问答系统API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, dict] = {}

SENSITIVE_OPS = {
    "add_product",
    "delete_product",
    "delete_product_by_name",
    "update_product",
    "add_products",
    "delete_products",
}


class ParseRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None


class ParseResponse(BaseModel):
    status: str
    result: Optional[str] = None
    operation: Optional[str] = None
    arguments: Optional[dict] = None
    session_id: Optional[str] = None


class ExecuteRequest(BaseModel):
    session_id: str
    password: str


class ExecuteResponse(BaseModel):
    status: str
    result: Optional[str] = None
    message: Optional[str] = None


@app.on_event("startup")
def startup():
    init_database()


@app.post("/api/parse", response_model=ParseResponse)
async def parse_message(req: ParseRequest):
    """解析用户自然语言指令"""
    try:
        messages = list(req.history or [])
        messages.append({"role": "user", "content": req.message.strip()})
        calls_list, text_content = parse_llm_response(messages)
    except Exception as e:
        return ParseResponse(status="error", result=f"解析失败：{str(e)}")

    if calls_list is None:
        return ParseResponse(status="direct_result", result=text_content or "")

    need_pw_calls = [(fn, args) for fn, args in calls_list if fn in SENSITIVE_OPS]
    if need_pw_calls:
        func_name, result_or_args = need_pw_calls[0]
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"operation": func_name, "arguments": result_or_args}
        return ParseResponse(
            status="need_password",
            operation=func_name,
            arguments=result_or_args,
            session_id=session_id,
        )

    results = []
    for func_name, result_or_args in calls_list:
        try:
            func = getattr(db_ops, func_name, None)
            if func is None:
                results.append(f"未知函数：{func_name}")
            else:
                results.append(func(**result_or_args))
        except Exception as e:
            results.append(f"执行失败：{str(e)}")
    return ParseResponse(status="direct_result", result="\n".join(results))


@app.post("/api/execute", response_model=ExecuteResponse)
async def execute_with_password(req: ExecuteRequest):
    """执行需要密码验证的操作"""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="会话无效或已过期")

    if not verify_password(req.password):
        return ExecuteResponse(status="error", message="密码错误")

    func_name = session["operation"]
    args = session["arguments"]
    try:
        func = getattr(db_ops, func_name)
        result = func(**args)
        del sessions[req.session_id]
        return ExecuteResponse(status="success", result=result)
    except Exception as e:
        return ExecuteResponse(status="error", message=f"执行失败：{str(e)}")


@app.get("/")
async def root():
    return {"message": "自然语言数据库问答系统API，请访问 /docs 查看文档"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
