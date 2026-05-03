# Day 30 复盘笔记 — 监控告警 + 生产最佳实践

## 今天学了什么

### 1. 为什么需要监控

```
没有监控：
服务挂了 → 用户投诉 → 你才知道（可能几小时后）

有监控：
服务挂了 → 监控发现 → 立刻发报警 → 3分钟内知道
```

---

### 2. 结构化日志

**普通日志：**
```
2026-05-03 03:00:00 - 请求完成 - 200
```

**结构化日志（JSON格式）：**
```json
{
  "timestamp": "2026-05-03T03:00:00",
  "level": "INFO",
  "message": "请求完成",
  "method": "POST",
  "path": "/ask",
  "status_code": 200,
  "latency_ms": 1250.5
}
```

**为什么用 JSON？** 日志系统（ELK、Datadog）能自动解析，支持搜索：
- 找出所有 latency_ms > 3000 的请求
- 找出所有 status_code = 500 的请求

**实现：**
```python
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data, ensure_ascii=False)
```

---

### 3. 中间件（Middleware）

**什么是中间件：** 拦截所有请求的处理器，在进入接口前后执行额外逻辑。

```
用户请求
    ↓
中间件（记录开始时间）
    ↓
你的接口（/ask、/health 等）
    ↓
中间件（记录耗时、写日志、更新统计）
    ↓
返回给用户
```

**代码：**
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)  # 处理真正的请求
    
    latency = time.time() - start_time
    logger.info("请求完成", extra={
        "path": request.url.path,
        "status_code": response.status_code,
        "latency_ms": round(latency * 1000, 2),
    })
    return response
```

**什么时候用中间件：**
```
✅ 适合：所有接口都需要做的事
   日志记录、请求统计、身份认证、跨域、限速、压缩

❌ 不适合：某个接口特有的逻辑（直接写在接口函数里）
```

**一句话记住：**
> 一件事需要在所有接口上做 → 用中间件
> 一件事只有某个接口需要 → 写在接口函数里

---

### 4. 健康检查接口

```python
@app.get("/health")
def health_check():
    checks = {}
    
    # 检查各组件
    try:
        model.invoke("ping")
        checks["llm"] = "ok"
    except Exception as e:
        checks["llm"] = f"error: {e}"
    
    checks["cache"] = "ok"
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return JSONResponse(
        status_code=200 if all_ok else 500,
        content={
            "status": "healthy" if all_ok else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
```

**谁来调用：** 监控系统每30秒自动探测一次
```
返回 200 → 正常
返回 500 → 异常 → 发告警
无响应   → 超时 → 发告警
```

**实测结果：**
```json
{"status":"healthy","checks":{"llm":"ok","cache":"ok"}}
```

---

### 5. 监控指标接口

```python
@app.get("/metrics")
def get_metrics():
    return {
        "total_requests": stats["total_requests"],
        "error_rate_percent": round(error_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
    }
```

**告警阈值参考：**
```
错误率 > 5%    → 有问题，需要排查
平均延迟 > 3秒  → 太慢，需要优化
```

**实测结果：**
```json
{
  "total_requests": 3,
  "error_rate_percent": 33.33,
  "avg_latency_ms": 863.54
}
```

---

### 6. 生产环境最佳实践清单

```
✅ 结构化日志（JSON格式）
✅ 中间件统一记录请求日志
✅ /health 健康检查接口
✅ /metrics 监控指标接口
✅ LLM 缓存（Day 28）
✅ API Key 认证（Day 28）
✅ 请求频率限制（Day 28）
✅ 输入校验（Day 28）
✅ LangSmith 追踪（Day 25）
⬜ Docker 容器化（Day 29 概念）
⬜ Nginx 反向代理（Day 29 概念）
⬜ CI/CD 自动部署（Day 29 概念）
```

---

## 面试考点

**Q：生产环境的 API 需要做哪些事？**  
答：安全层（API Key认证、频率限制、输入校验）、性能层（LLM缓存、异步处理）、可观测层（结构化日志、健康检查、监控指标）、部署层（Docker容器化、Nginx反向代理、CI/CD）。

**Q：什么是中间件？什么时候用？**  
答：拦截所有请求的处理器，在进入接口前后执行额外逻辑。适合所有接口都需要做的事：日志记录、请求统计、身份认证、限速等。不适合某个接口特有的逻辑。

**Q：健康检查接口的作用？**  
答：监控系统定时探测这个接口，返回200表示正常，返回500触发告警。接口内部检查各个依赖组件（LLM、数据库、缓存）是否正常，任一异常就返回500。

**Q：结构化日志和普通日志的区别？**  
答：结构化日志用JSON格式，每个字段都有固定的key，日志系统能自动解析和检索。普通文本日志只能全文搜索，无法按字段过滤。生产环境排查问题时，结构化日志效率高10倍以上。

---

## 今日文件结构
```
week5/day30/
└── 01_monitoring.py  ✅ 结构化日志、中间件、健康检查、监控指标
```