# FastAPI Day 7 — 项目结构 + 测试 + Docker 部署

## 1. 标准项目结构

```
fastapi-learn/
├── app/
│   ├── main.py        ← FastAPI 实例，注册所有路由
│   ├── database.py    ← 数据库连接配置
│   ├── models.py      ← SQLAlchemy 数据库模型
│   ├── schemas.py     ← Pydantic API 模型
│   ├── auth.py        ← 认证逻辑
│   └── routers/
│       ├── __init__.py
│       └── users.py   ← 用户相关接口
├── tests/
│   ├── __init__.py
│   └── test_users.py  ← 接口测试
├── Dockerfile
└── requirements.txt
```

**main.py 是"总线"**，把所有路由组装在一起，其他文件各司其职。

---

## 2. requirements.txt — 依赖管理

```bash
# 生成依赖文件
pip freeze > requirements.txt

# 在新环境安装所有依赖
pip install -r requirements.txt
```

作用：记录项目所有依赖包和版本，换机器或部署时一键安装，保证环境一致。

---

## 3. 接口测试

### 测试原理

```
test_users.py
    ↓ from main import app
main.py（已注册所有路由）
    ↓ app.include_router(users.router)
routers/users.py
    ↓ 所有接口
/users/login、/users/me、/users/{id}...
```

`TestClient` 把 app 包起来模拟"假浏览器"，不需要真正启动服务器就能测试所有接口。

### 测试代码

```python
# tests/test_users.py
from fastapi.testclient import TestClient
import sys, os

# 把根目录加入 Python 模块搜索路径，让 from main import app 能找到文件
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_login_success():
    res = client.post("/users/login?username=admin&password=123")
    assert res.status_code == 200       # 断言状态码是 200
    assert "token" in res.json()        # 断言返回里有 token 字段

def test_login_fail():
    res = client.post("/users/login?username=admin&password=wrong")
    assert res.status_code == 401       # 密码错误应该返回 401

def test_me_without_token():
    res = client.get("/users/me")
    assert res.status_code == 401       # 不带 Token 应该返回 401

def test_create_user():
    res = client.post("/users/", json={"username": "testuser", "email": "test@test.com"})
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"
```

### 运行测试

```bash
pip install pytest httpx
pytest tests/test_users.py -v    # -v 显示每个测试详细结果
```

### assert 的作用

`assert 条件` — 断言这个条件必须为真，不满足就报错测试失败。

```python
assert res.status_code == 200       # 状态码必须是 200
assert "token" in res.json()        # 返回 JSON 里必须有 token
assert res.json()["username"] == "testuser"  # username 值必须正确
```

---

## 4. sys.path.append 说明

```python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

测试文件在 `tests/` 子目录，Python 默认只在当前目录找模块。这行代码把上一层根目录加入搜索路径，让 `from main import app` 能找到根目录下的 `main.py`。

---

## 5. Docker 部署

### Docker 是什么

把代码 + 运行环境打包成"集装箱"（镜像），在任何机器上运行结果完全一致。

```
没有 Docker：换机器 → 重新装 Python → 重新 pip install → 手动启动
有了 Docker：换机器 → docker run → 直接跑
```

### Dockerfile

```dockerfile
FROM python:3.11-slim
# 基础镜像，使用已装好 Python 3.11 的精简系统

WORKDIR /app
# 设置工作目录，后续命令都在 /app 里执行

COPY requirements.txt .
# 先只复制依赖文件（利用 Docker 缓存层，依赖没变就不重新安装）

RUN pip install -r requirements.txt
# 安装所有依赖

COPY . .
# 复制项目所有文件进容器

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 启动命令
```

### 为什么 host 必须是 0.0.0.0

- `127.0.0.1` — 只有本机能访问，容器外访问不到
- `0.0.0.0` — 监听所有网络接口，容器外可以访问

Docker 容器是一个隔离的小机器，用 `127.0.0.1` 只有容器内部能连，宿主机访问不到。

### 常用 Docker 命令

```bash
docker build -t fastapi-learn .        # 构建镜像
docker run -p 8000:8000 fastapi-learn  # 运行容器，映射端口
docker ps                              # 查看运行中的容器
docker stop <容器id>                   # 停止容器
```

---

## 6. 面试常见问题

**Q: 如何给依赖注入的 get_db 在测试时替换成测试数据库？**
> 使用 `app.dependency_overrides`，把 `get_db` 替换成返回测试数据库 Session 的函数，测试结束后清空覆盖，避免污染生产数据库。

**Q: FastAPI 项目上线前要做哪些配置？**
> 关闭自动文档（`docs_url=None`）、SECRET_KEY 存环境变量、配置 CORS、使用生产数据库（PostgreSQL）、关闭 `--reload`。

**Q: 你会怎么做接口的版本管理？**
> 用 APIRouter 的 prefix 加版本号：`APIRouter(prefix="/api/v1/users")`，新版本单独建路由文件，老版本继续维护，互不影响。