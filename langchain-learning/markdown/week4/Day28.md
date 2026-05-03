# Day 28 复盘笔记 — 缓存优化 + 安全加固

## 今天学了什么

### 1. 为什么需要缓存

```
不用缓存：
同一个问题问两次 → 调两次 LLM → 花两倍时间和钱

用缓存：
第一次 → 调 LLM → 存缓存
第二次 → 命中缓存 → 直接返回（0ms，不花钱）
```

### 2. LLM 缓存接入（两行搞定）

```python
from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# 内存缓存（开发用，重启丢失）
set_llm_cache(InMemoryCache())
```

**实测效果：**
```
第一次：1.14s（调 LLM）
第二次：0.00s（命中缓存）
速度提升：366x
```

**生产环境用 SQLite 持久化缓存：**
```python
from langchain_community.cache import SQLiteCache
set_llm_cache(SQLiteCache(database_path="llm_cache.db"))
# 重启后缓存还在！
```

### 3. API Key 认证

```python
from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException

API_KEYS = {os.getenv("API_KEY", "dev-key-123")}
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="无效的 API Key")
    return api_key

# 接口加认证
@app.post("/secure/detect")
def detect(body: Request, api_key: str = Depends(verify_api_key)):
    ...
```

**用户调用时需要在请求头加：**
```
X-API-Key: your-api-key
```

### 4. 请求频率限制（Rate Limiting）

```python
from collections import defaultdict

request_counts = defaultdict(list)
RATE_LIMIT = 10   # 每分钟最多10次
RATE_WINDOW = 60  # 60秒窗口

def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    # 清理过期记录
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if now - t < RATE_WINDOW
    ]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="请求太频繁！")
    
    request_counts[client_ip].append(now)
```

**429 状态码**表示"Too Many Requests"，是 Rate Limiting 的标准响应码。

### 5. 输入校验（防注入攻击）

```python
class SafeRequest(BaseModel):
    image_path: str
    
    def validate_path(self):
        # 防路径注入
        dangerous = ["..", "//", "\\\\", "/etc", "C:\\Windows"]
        for d in dangerous:
            if d in self.image_path:
                raise HTTPException(400, f"非法路径：{d}")
        
        # 限制文件类型
        if not self.image_path.lower().endswith(
            ('.jpg', '.jpeg', '.png', '.bmp')
        ):
            raise HTTPException(400, "只支持图片格式")
```

**测试结果：**
```
../../../etc/passwd → 🛡️ 已拦截（路径注入）
test.exe           → 🛡️ 已拦截（非图片格式）
normal/image.jpg   → ✅ 通过
```

---

## 生产环境安全清单

```
✅ API Key 认证       → 防止未授权访问
✅ 请求频率限制       → 防止 DDoS 和滥用
✅ 输入校验           → 防止路径注入、文件类型攻击
✅ LLM 缓存           → 降低成本、提升响应速度
⬜ HTTPS              → 加密传输（部署时配置）
⬜ 日志审计           → 记录所有请求（配合 LangSmith）
⬜ 敏感信息脱敏       → 日志里不记录 API Key
```

---

## 缓存方案对比

| 方案 | 优点 | 缺点 | 适合场景 |
|------|------|------|---------|
| InMemoryCache | 极快，零依赖 | 重启丢失 | 开发测试 |
| SQLiteCache | 持久化，轻量 | 单机，不能分布式 | 单机生产 |
| RedisCache | 分布式，高性能 | 需要部署 Redis | 多机生产 |

---

## 面试考点

**Q：怎么减少 LLM 调用的成本？**  
答：语义缓存——相同或相似的请求直接返回缓存结果，不调 LLM。LangChain 提供 `set_llm_cache()` 两行接入，支持内存、SQLite、Redis 等多种后端。

**Q：API 安全怎么做？**  
答：三层防护：API Key 认证（防未授权）、Rate Limiting（防滥用/DDoS）、输入校验（防注入攻击）。生产环境还要加 HTTPS 和日志审计。

**Q：Rate Limiting 的原理？**  
答：滑动窗口算法——记录每个 IP 在最近 N 秒内的请求次数，超过阈值返回 429。简单实现用内存字典，生产环境用 Redis 保证多实例共享。

---

## 今日文件结构
```
week4/day28/
└── 01_cache_security.py  ✅ LLM缓存、API Key认证、频率限制、输入校验
```

---

## Week 4 完结！

四周学习总结：
```
Week 1 → LLM API + LangChain 基础 + 第一个 Agent
Week 2 → 完整 RAG 系统（加载→检索→重排→评估）
Week 3 → Agent 进阶（HIL/MCP/Plan-Execute/Reflexion/多Agent）
Week 4 → 生产化（子图/并行/长期记忆/LangSmith/刹车片Agent/缓存/安全）
```

拥有三个完整项目：
- PDF 问答 RAG 系统
- 多 Agent 研究助手  
- 刹车片检测 Agent API（最有差异化竞争力）