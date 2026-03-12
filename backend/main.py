"""
FastAPI 后端：自然语言数据库问答 API（复用项目根目录的 config、db、llm、auth）
运行方式：在项目根目录执行  uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations
import sys
from pathlib import Path

# 将项目根目录加入路径，以便复用根目录的模块
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import uuid
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db_connection import init_database
import db_operations as db_ops
from llm_client import parse_llm_response
from auth import verify_password_input as verify_password

app = FastAPI(title="NL2SQL API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}
SESSION_TTL = 300
SENSITIVE_OPS = {"add_product", "add_products", "delete_product", "delete_products", "delete_product_by_name", "update_product"}
FUNCTION_MAP = {
    "add_product": db_ops.add_product,
    "add_products": db_ops.add_products,
    "delete_product": db_ops.delete_product,
    "delete_products": db_ops.delete_products,
    "delete_product_by_name": db_ops.delete_product_by_name,
    "update_product": db_ops.update_product,
    "query_products": db_ops.query_products,
}


def _clean_expired_sessions():
    now = time.time()
    expired = [sid for sid, data in SESSIONS.items() if now - data["created_at"] > SESSION_TTL]
    for sid in expired:
        del SESSIONS[sid]


class ParseRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None


class ExecuteRequest(BaseModel):
    session_id: str
    password: str


@app.on_event("startup")
def startup():
    init_database()


@app.post("/api/parse")
def api_parse(req: ParseRequest):
    _clean_expired_sessions()
    messages = list(req.history or [])
    messages.append({"role": "user", "content": req.message.strip()})
    calls_list, text_content = parse_llm_response(messages)
    if calls_list is None:
        return {"status": "direct_result", "result": text_content}
    need_pw_calls = [(fn, args) for fn, args in calls_list if fn in SENSITIVE_OPS]
    if need_pw_calls:
        fn, args = need_pw_calls[0]
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {"operation": fn, "arguments": args, "created_at": time.time()}
        return {"status": "need_password", "operation": fn, "arguments": args, "session_id": session_id}
    results = []
    for fn, args in calls_list:
        if fn in FUNCTION_MAP:
            try:
                results.append(FUNCTION_MAP[fn](**args))
            except Exception as e:
                results.append(f"执行 {fn} 出错：{str(e)}")
        else:
            results.append(f"未知函数：{fn}")
    return {"status": "direct_result", "result": "\n".join(results)}


@app.post("/api/execute")
def api_execute(req: ExecuteRequest):
    _clean_expired_sessions()
    sid = req.session_id
    if sid not in SESSIONS:
        return {"status": "error", "message": "会话无效或已过期"}
    if not verify_password(req.password):
        return {"status": "error", "message": "密码错误"}
    data = SESSIONS.pop(sid)
    fn, args = data["operation"], data["arguments"]
    if fn not in FUNCTION_MAP:
        return {"status": "error", "message": "未知操作"}
    try:
        result = FUNCTION_MAP[fn](**args)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/health")
def health():
    return {"status": "ok"}
