# FastAPI Day 1 — 环境搭建 + 第一个接口

## 1. FastAPI 是什么

FastAPI 是一个用 Python 写"接口"的框架。

> 可以把它理解成一个**信箱系统**：前端（网页/App）发请求过来，FastAPI 负责接收、处理、返回数据。

---

## 2. 安装与启动

```bash
# 安装依赖
pip install fastapi uvicorn

# 验证安装
python -c "import fastapi; print(fastapi.__version__)"

# 启动服务（--reload 代码改动后自动重启，开发时使用）
uvicorn main:app --reload
```

---

## 3. 第一个接口

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello FastAPI"}
```

- `app = FastAPI()` — 创建应用实例
- `@app.get("/")` — 路由装饰器，`GET` 方法，路径是 `/`
- 函数返回字典，FastAPI 自动转成 JSON

---

## 4. 路径参数 vs 查询参数

```python
@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None):
    return {"id": item_id, "query": q}
```

| 类型 | 写法 | URL 示例 |
|------|------|----------|
| 路径参数 | `{item_id}` + 函数同名参数 | `/items/42` |
| 查询参数（可选） | 函数参数加 `= None` | `/items/42?q=hello` |
| 查询参数（必填） | 函数参数不加默认值 | 不传则返回 422 错误 |

**规则**：函数参数名出现在 `{}` 里 → 路径参数；否则 → 查询参数。

---

## 5. 默认值的作用

```python
q: str = None   # 可选，不传默认为 None
q: str          # 必填，不传报 422 Field required
```

---

## 6. 自动文档

FastAPI 自动生成交互式文档，无需额外配置：

| 地址 | 说明 |
|------|------|
| `http://127.0.0.1:8000/docs` | Swagger UI，可直接在页面测试接口 |
| `http://127.0.0.1:8000/redoc` | ReDoc 风格文档 |

---

## 7. 练习题（自己完成）

```python
# 要求：
# 路径 /users/{username}
# 可选查询参数 age（整数，默认 None）
# 返回 {"username": "xxx", "age": xxx}

@app.get("/users/{username}")
def get_username(username: str, age: int = None):
    return {"username": username, "age": age}
```

---

## 8. 面试常见问题

**Q: FastAPI 和 Flask 的区别是什么？**
> FastAPI 基于 ASGI（异步），Flask 基于 WSGI（同步）；FastAPI 有自动数据校验和自动文档，性能更高。

**Q: FastAPI 为什么性能比 Flask 好？**
> FastAPI 使用 ASGI + 异步支持，能同时处理更多请求；Flask 是同步阻塞模型，一次只处理一个请求。

---

## 9. 完整 main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello FastAPI"}

@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None):
    return {"id": item_id, "query": q}

@app.get("/users/{username}")
def get_username(username: str, age: int = None):
    return {"username": username, "age": age}

# 启动命令：uvicorn main:app --reload
```