# FastAPI Day 5 — JWT 认证 + 接口鉴权

## 1. 为什么用 JWT 而不是 Session

| | Session | JWT |
|---|---|---|
| 状态 | 服务器存储 Session | 服务器不存任何东西 |
| 扩展性 | 多台服务器需要同步 | 无状态，天然支持分布式 |
| 适合场景 | 传统网页应用 | 现代 API / 前后端分离 |

---

## 2. JWT 工作流程

```
1. 用户发送用户名 + 密码
2. 服务器验证通过 → 生成 Token 返回
3. 用户每次请求都在 Header 里带上 Token
4. 服务器验证 Token 合法 → 放行
```

---

## 3. JWT 结构原理

Token 长这样，由三段组成，用 `.` 分隔：

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.xxxxx
      头部（算法）          payload（用户信息）    签名
```

**重要：JWT 是"签名"不是"加密"**

- payload 是明文，任何人都能解码看到内容
- SECRET_KEY 的作用是"验证签名是不是我签的"，防止伪造
- 验证时：用 SECRET_KEY 对 payload 重新算签名，和 Token 里的签名比对，一致则合法

类比：公章 —— 不同文件可以盖同一个章，验证时看章是不是真的，不看文件内容。

---

## 4. SECRET_KEY 说明

```python
SECRET_KEY = "fastapi-learn-secret"
```

- 生成 Token 和验证 Token 必须用同一个 KEY
- 如果 KEY 泄露，攻击者可以伪造任意 Token
- ⚠ 实际项目必须存在环境变量里，不能硬编码：

```python
import os
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key")
```

---

## 5. auth.py — Token 核心逻辑

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "fastapi-learn-secret"
ALGORITHM = "HS256"

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=1)  # 1小时后过期
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None  # Token 无效或过期返回 None
```

- `exp` — expiration，过期时间，超时后 Token 自动失效
- `verify_token` 失败返回 None，接口层再处理 401

---

## 6. OAuth2PasswordBearer — Token 提取器

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
```

两个作用：
1. **自动从请求头提取 Token**：前端发 `Authorization: Bearer xxxtoken`，它帮你拿出 Token 字符串
2. **告诉 `/docs` 文档**登录地址在哪，让文档页面出现 Authorize 按钮

配合 Depends 使用，不需要手动解析请求头。

---

## 7. 受保护接口的完整写法

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import create_token, verify_token

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Step 1: 定义"验证 Token"的依赖函数
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效Token")
    return payload["sub"]  # 返回用户名

# Step 2: 登录接口，返回 Token
@router.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "123":
        token = create_token({"sub": username})
        return {"token": token}
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# Step 3: 受保护接口，必须登录才能访问
@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
```

---

## 8. 路由顺序陷阱 ⚠

```python
# ❌ 错误顺序 —— /me 会被 /{user_id} 先匹配，把 "me" 当成整数解析报错
@router.get("/{user_id}")
def get_user(user_id: int, ...): ...

@router.get("/me")
def get_me(...): ...

# ✅ 正确顺序 —— 具体路径放前面，动态路径放后面
@router.get("/me")
def get_me(...): ...

@router.get("/{user_id}")
def get_user(user_id: int, ...): ...
```

**FastAPI 路由按顺序匹配，具体路径必须放在动态路径前面。**

---

## 9. 测试方式（PowerShell）

```powershell
# 第一步：登录拿 Token
Invoke-WebRequest -Uri "http://127.0.0.1:8000/users/login?username=admin&password=123" -Method POST

# 第二步：带 Token 访问受保护接口
Invoke-WebRequest -Uri "http://127.0.0.1:8000/users/me" -Method GET -Headers @{Authorization="Bearer 你的Token"}
```

---

## 10. 易错点

- Token 过期后需要重新登录，不会自动续期
- SECRET_KEY 要存环境变量，不能硬编码进代码
- OAuth2PasswordBearer 只是提取 Token 的工具，验证逻辑要自己写
- `/me` 这类具体路径必须放在 `/{user_id}` 这类动态路径前面

---

## 11. 面试常见问题

**Q: JWT 的组成结构是什么？payload 里能存什么？**
> JWT 由头部、payload、签名三段组成，用 `.` 分隔。payload 里可以存用户 id、用户名、角色等非敏感信息，不能存密码——因为 payload 是明文，任何人都能解码。

**Q: Token 失效了怎么处理？**
> Token 过期后接口返回 401，前端检测到 401 后跳转登录页让用户重新登录获取新 Token。进阶方案是用 refresh token 机制自动续期。

**Q: 中间件和依赖注入有什么区别？**
> 中间件对所有请求生效，依赖注入只对加了 Depends 的接口生效。鉴权逻辑用依赖注入更灵活，可以精确控制哪些接口需要登录。