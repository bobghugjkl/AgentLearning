import os
import time
import hashlib
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

# 改成：
from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain_core.messages import HumanMessage

load_dotenv()

app = FastAPI(title="刹车片 Agent API - 生产加固版")

# ── 缓存初始化 ────────────────────────────────────
# 方案1：内存缓存（开发用，重启丢失）
set_llm_cache(InMemoryCache())
print("✅ LLM 内存缓存已启用")

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# ── 测试缓存效果 ──────────────────────────────────
print("\n=== 测试 LLM 缓存 ===")

question = "用一句话介绍LangChain"

print("第一次调用（无缓存）...")
start = time.time()
r1 = model.invoke(question)
t1 = time.time() - start
print(f"耗时：{t1:.2f}s，回答：{r1.content[:50]}")

print("\n第二次调用（命中缓存）...")
start = time.time()
r2 = model.invoke(question)
t2 = time.time() - start
print(f"耗时：{t2:.2f}s，回答：{r2.content[:50]}")

print(f"\n速度提升：{t1/max(t2,0.001):.0f}x")

# ── 安全加固 ──────────────────────────────────────

# 1. API Key 认证
API_KEYS = {
    os.getenv("API_KEY", "dev-key-123"),  # 从环境变量读取
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Depends(api_key_header)):
    """验证 API Key"""
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="无效的 API Key，请在请求头添加 X-API-Key"
        )
    return api_key


# 2. 请求频率限制（简单版）
from collections import defaultdict
import time

request_counts = defaultdict(list)  # {ip: [时间戳列表]}
RATE_LIMIT = 10  # 每分钟最多10次
RATE_WINDOW = 60  # 60秒窗口


def check_rate_limit(request: Request):
    """检查请求频率"""
    client_ip = request.client.host
    now = time.time()

    # 清理60秒前的记录
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if now - t < RATE_WINDOW
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"请求太频繁！每分钟最多 {RATE_LIMIT} 次"
        )

    request_counts[client_ip].append(now)


# 3. 输入校验
class SafeRequest(BaseModel):
    image_path: str
    instruction: str = "检测刹车片型号"

    def validate_path(self):
        """防止路径注入攻击"""
        dangerous = ["..", "//", "\\\\", "/etc", "C:\\Windows"]
        for d in dangerous:
            if d in self.image_path:
                raise HTTPException(
                    status_code=400,
                    detail=f"非法路径：包含危险字符 {d}"
                )
        if not self.image_path.lower().endswith(
                ('.jpg', '.jpeg', '.png', '.bmp')
        ):
            raise HTTPException(
                status_code=400,
                detail="只支持图片格式：jpg/jpeg/png/bmp"
            )


# ── 加固后的接口 ──────────────────────────────────
@app.post("/secure/detect")
def secure_detect(
        body: SafeRequest,
        request: Request,
        api_key: str = Depends(verify_api_key),
):
    """加固版检测接口：需要 API Key + 频率限制 + 输入校验"""
    # 输入校验
    body.validate_path()
    # 频率限制
    check_rate_limit(request)

    if not os.path.exists(body.image_path):
        raise HTTPException(status_code=400, detail="图片文件不存在")

    # 调用 LLM（有缓存加速）
    response = model.invoke(
        f"图片路径：{body.image_path}，任务：{body.instruction}"
    )

    return {
        "status": "success",
        "result": response.content,
        "cached": True,  # 生产环境可以检测是否真正命中缓存
    }


# ── 测试安全功能 ──────────────────────────────────
print("\n=== 测试输入校验 ===")

test_cases = [
    ("../../../etc/passwd", "路径注入攻击"),
    ("test.exe", "非图片格式"),
    ("normal/path/image.jpg", "正常路径"),
]

for path, desc in test_cases:
    req = SafeRequest(image_path=path)
    try:
        req.validate_path()
        print(f"✅ {desc}：通过校验")
    except HTTPException as e:
        print(f"🛡️ {desc}：已拦截 - {e.detail}")