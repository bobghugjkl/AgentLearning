# FastAPI Day 3 — 路由组织 + 依赖注入

## 1. 为什么要拆分路由

所有接口写在一个 `main.py` 里会导致：
- 代码臃肿难维护
- 多人协作时频繁冲突
- 不同模块逻辑混在一起

**APIRouter 就是用来把不同模块的接口拆分到不同文件里的。**

---

## 2. 项目结构

```
fastapi-learn/
├── main.py
├── schemas.py
└── routers/
    ├── __init__.py    ← 空文件，让 Python 识别这是一个包
    └── users.py
```

---

## 3. APIRouter 基本用法

```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def list_users():
    return {"users": []}

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

- `prefix="/users"` — 该文件下所有接口路径自动加上 `/users` 前缀
- `tags=["users"]` — `/docs` 文档里自动按 tag 分组

| 装饰器 | 实际路径 |
|--------|----------|
| `@router.get("/")` | `/users/` |
| `@router.get("/{user_id}")` | `/users/{user_id}` |

---

## 4. 注册路由到 main.py

```python
# main.py
from fastapi import FastAPI
from routers import users

app = FastAPI()

app.include_router(users.router)
```

---

## 5. 依赖注入（Depends）

**核心作用：把公共逻辑提取出来，所有接口复用，改一处全生效。**

```python
# routers/users.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/users", tags=["users"])

def common_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@router.get("/")
def list_users(params: dict = Depends(common_params)):
    return {"params": params, "users": []}
```

---

## 6. Depends 的执行时机

⚠ **每次请求到来时执行一次，不是服务器启动时执行。**

适合放进 Depends 的逻辑：
- 公共分页参数
- 验证 Token（Day 5 会用到）
- 获取数据库连接（Day 4 会用到）

---

## 7. 请求体 + Depends 同时使用

```python
from schemas import User

@router.post("/")
def create_user(user: User, params: dict = Depends(common_params)):
    return {"params": params, "user": user}
```

- `user: User` — 请求体，从 JSON Body 里解析
- `params: dict = Depends(common_params)` — 依赖注入，从查询参数里解析

两个参数分开写，互不干扰。

---

## 8. 面试常见问题

**Q: FastAPI 的依赖注入和 Spring 的 DI 有什么相似之处？**
> 两者都是把公共逻辑/对象提取出来统一管理，需要用的地方直接声明，框架自动注入，不需要手动创建。

**Q: 为什么要用 APIRouter 而不是全写在 main.py？**
> 代码拆分、职责清晰、便于维护和多人协作。每个模块独立管理自己的路由，main.py 只负责组装。

---

## 9. 完整 routers/users.py

```python
from fastapi import APIRouter, Depends
from schemas import User

router = APIRouter(prefix="/users", tags=["users"])

def common_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@router.get("/")
def list_users(params: dict = Depends(common_params)):
    return {"params": params, "users": []}

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@router.post("/")
def create_user(user: User, params: dict = Depends(common_params)):
    return {"params": params, "user": user}
```