# FastAPI Day 6 — 异步编程 + 后台任务

## 1. 同步 vs 异步

**同步模式的问题：**

一个接口需要等待 3 秒，100 个并发请求时：
- 第 1 个用户等 3 秒
- 第 2 个用户等 6 秒
- 第 100 个用户等 300 秒 ← 服务器被"堵死"

**异步的解决方式：等待时让出控制权，去处理其他请求**

类比服务员：点完单去下单，等菜的时候去服务另一桌，菜好了再回来上菜。不是分身，而是合理利用等待时间。

---

## 2. async def vs 普通 def

| | 使用场景 | 例子 |
|---|---|---|
| `async def` | IO 密集型（需要等待） | 网络请求、数据库查询、文件读写 |
| 普通 `def` | CPU 密集型（需要计算） | 图像处理、数据加密、复杂数学运算 |

**CPU 密集型任务用 `async def` 没有效果**，因为没有"等待"可以让出，async 对它无意义。

---

## 3. 代码对比

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

# 同步 —— 阻塞整个服务器 2 秒
@app.get("/sync")
def sync_route():
    time.sleep(2)        # 堵死服务器，其他请求全部等待
    return {"done": "sync"}

# 异步 —— 等待时让出控制权，其他请求可以继续处理
@app.get("/async")
async def async_route():
    await asyncio.sleep(2)   # 等待期间服务器可以处理其他请求
    return {"done": "async"}
```

---

## 4. 最重要的易错点 ⚠

**`async def` 里不能直接调用同步阻塞函数！**

```python
# ❌ 错误 —— async 里用了同步 sleep，反而堵死整个事件循环
async def bad_route():
    time.sleep(2)        # 这会把整个服务器堵死！
    return {"done": "bad"}

# ✅ 正确 —— async 里要用 await + 异步版本
async def good_route():
    await asyncio.sleep(2)   # 等待时让出控制权
    return {"done": "good"}
```

---

## 5. BackgroundTasks — 后台任务

**解决问题：** 用户注册后要发邮件，发邮件需要 3 秒。不能让用户等 3 秒，应该立即返回，后台慢慢发。

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_email(to: str, content: str):
    time.sleep(3)   # 模拟耗时操作
    print(f"邮件已发送给 {to}：{content}")

@app.post("/register")
async def register(email: str, bg: BackgroundTasks):
    bg.add_task(send_email, email, "欢迎注册！")   # 加入后台任务
    return {"status": "注册成功，欢迎邮件发送中..."}  # 立即返回
```

执行顺序：
1. 请求进来 → 把 `send_email` 加入后台队列
2. **立即返回** `{"status": "注册成功..."}` 给用户
3. 后台异步执行 `send_email`，3 秒后打印结果

---

## 6. BackgroundTasks vs Celery

| | BackgroundTasks | Celery |
|---|---|---|
| 适合场景 | 简单后台任务，开发测试 | 生产环境，高可靠性 |
| 任务丢失 | 服务器重启后任务丢失 | 任务持久化，不丢失 |
| 依赖 | FastAPI 内置，无需额外安装 | 需要 Redis/RabbitMQ |

**⚠ BackgroundTasks 在生产环境不可靠，重要任务（发邮件、支付回调）要用 Celery。**

---

## 7. 面试常见问题

**Q: FastAPI 的异步和 Node.js 的异步有什么相似之处？**
> 两者都是基于事件循环（Event Loop）的单线程异步模型，IO 等待时让出控制权处理其他请求，而不是开多线程阻塞等待。

**Q: 什么场景下 async def 不会带来性能提升？**
> CPU 密集型任务，如图像处理、大量数学计算。这类任务没有 IO 等待，async 无法让出控制权，和同步没有区别。CPU 密集任务应该用多进程（multiprocessing）来解决。

**Q: BackgroundTasks 和 Celery 的区别？**
> BackgroundTasks 是 FastAPI 内置的轻量后台任务，简单易用但不可靠——服务器重启任务丢失。Celery 是专业任务队列，支持任务持久化、重试、定时任务，适合生产环境。

---

## 8. 完整 main.py

```python
from fastapi import FastAPI, BackgroundTasks
from routers import users
from database import engine
from models import Base
import asyncio
import time

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)

# 同步接口
@app.get("/sync")
def sync_route():
    time.sleep(2)
    return {"done": "sync"}

# 异步接口
@app.get("/async")
async def async_route():
    await asyncio.sleep(2)
    return {"done": "async"}

# 后台任务
def send_email(to: str, content: str):
    time.sleep(3)
    print(f"邮件已发送给 {to}：{content}")

@app.post("/register")
async def register(email: str, bg: BackgroundTasks):
    bg.add_task(send_email, email, "欢迎注册！")
    return {"status": "注册成功，欢迎邮件发送中..."}
```