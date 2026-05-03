import os
import time
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

load_dotenv()


# ── 结构化日志 ─────────────────────────────────────
class JSONFormatter(logging.Formatter):
    """把日志格式化成 JSON，方便日志系统解析"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        # 如果有额外字段就加进去
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data, ensure_ascii=False)


# 配置日志
logger = logging.getLogger("brake_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# ── 统计数据 ───────────────────────────────────────
stats = {
    "total_requests": 0,
    "success_requests": 0,
    "error_requests": 0,
    "total_latency": 0.0,
}

# ── 初始化 ─────────────────────────────────────────
set_llm_cache(InMemoryCache())
app = FastAPI(title="刹车片 API - 监控版")

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)


# ── 中间件：记录每次请求 ────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """拦截所有请求，记录日志和统计"""
    start_time = time.time()
    stats["total_requests"] += 1

    # 处理请求
    try:
        response = await call_next(request)
        latency = time.time() - start_time
        stats["total_latency"] += latency

        # 成功
        if response.status_code < 400:
            stats["success_requests"] += 1
        else:
            stats["error_requests"] += 1

        # 结构化日志
        logger.info(
            "请求完成",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": round(latency * 1000, 2),
            }
        )
        return response

    except Exception as e:
        stats["error_requests"] += 1
        logger.error(
            "请求异常",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
            }
        )
        raise


# ── 健康检查接口 ───────────────────────────────────
@app.get("/health")
def health_check():
    """
    监控系统每30秒来探测一次这个接口
    返回200 → 服务正常
    返回500 → 服务异常 → 触发告警
    """
    # 检查各个组件是否正常
    checks = {}

    # 检查1：LLM 是否可用
    try:
        model.invoke("ping")
        checks["llm"] = "ok"
    except Exception as e:
        checks["llm"] = f"error: {e}"

    # 检查2：缓存是否正常
    checks["cache"] = "ok"

    # 如果有任何组件异常，返回500
    all_ok = all(v == "ok" for v in checks.values())

    status_code = 200 if all_ok else 500
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_ok else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ── 监控指标接口 ───────────────────────────────────
@app.get("/metrics")
def get_metrics():
    """返回服务的运行统计数据"""
    total = stats["total_requests"]
    avg_latency = (
        stats["total_latency"] / total * 1000
        if total > 0 else 0
    )
    error_rate = (
        stats["error_requests"] / total * 100
        if total > 0 else 0
    )

    return {
        "total_requests": total,
        "success_requests": stats["success_requests"],
        "error_requests": stats["error_requests"],
        "error_rate_percent": round(error_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
    }


# ── 普通接口 ───────────────────────────────────────
class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(body: Question):
    response = model.invoke(body.question)
    return {"answer": response.content}


print("服务启动完成！")
print("健康检查：http://127.0.0.1:8002/health")
print("监控指标：http://127.0.0.1:8002/metrics")