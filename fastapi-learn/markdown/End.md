# FastAPI 7天面试题总复习

---

## Day 1 — 基础路由

**Q: FastAPI 和 Flask 的区别是什么？**
> FastAPI 基于 ASGI（异步），Flask 基于 WSGI（同步）。FastAPI 有自动类型校验、自动生成文档，性能更高，适合高并发 API 开发。Flask 更轻量，生态更成熟。

**Q: 路径参数和查询参数有什么区别？怎么定义？**
> 路径参数写在路径的 `{}` 里，函数参数同名即可；查询参数直接写函数参数，加默认值就是可选。
```python
@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None): ...
# 访问：/items/42?q=hello
```

**Q: /docs 是怎么来的？需要额外配置吗？**
> FastAPI 自动根据接口定义生成 OpenAPI 文档，访问 `/docs` 是 Swagger UI，`/redoc` 是另一种风格。不需要任何额外配置，零代码实现。

---

## Day 2 — Pydantic 校验

**Q: Pydantic 是用来做什么的？**
> 用来定义数据模型并自动做类型校验。请求体数据会自动经过 Pydantic 校验，类型不对或缺少必填字段时自动返回 422 错误，不需要手动写任何校验代码。

**Q: 422 错误是什么时候触发的？**
> 请求数据不符合 Pydantic 模型定义时触发：缺少必填字段、字段类型错误、不满足 Field 校验规则（如 `gt=0` 但传了负数）。

**Q: `Optional[str] = None` 和 `str` 有什么区别？**
> `str` 是必填字段，不传会报 422。`Optional[str] = None` 是可选字段，不传时默认为 None。两件事缺一不可：`Optional` 声明类型可以是 None，`= None` 提供默认值。

**Q: Field 常用参数有哪些？**
```python
Field(gt=0)          # 大于 0
Field(ge=0)          # 大于等于 0
Field(lt=100)        # 小于 100
Field(min_length=2)  # 字符串最短 2 位
Field(max_length=50) # 字符串最长 50 位
Field(default=None)  # 默认值
Field(description="说明文字")
```

---

## Day 3 — 路由与依赖注入

**Q: 为什么要用 APIRouter 而不是全写在 main.py？**
> 代码拆分、职责清晰、便于维护和多人协作。每个模块独立管理自己的路由，main.py 只负责组装。几十个接口全写一个文件会导致代码臃肿、多人协作冲突。

**Q: Depends 是用来做什么的？什么时候用？**
> 把公共逻辑提取出来，所有接口复用，改一处全生效。常见场景：公共分页参数、验证 Token（鉴权）、获取数据库连接。Depends 里的函数每次请求都会重新执行。

**Q: prefix 和 tags 分别有什么作用？**
> `prefix` 给该路由下所有接口自动加路径前缀，省得每个接口重复写。`tags` 让 `/docs` 文档自动按分组显示，方便查阅。

---

## Day 4 — 数据库 CRUD

**Q: FastAPI 中如何管理数据库 Session 的生命周期？**
> 用 `yield` 写法的 `get_db` 函数配合 `Depends`，每次请求自动创建 Session，请求结束后 `finally` 块自动关闭，确保不泄漏连接。
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Q: 为什么 get_db 用 yield 而不是 return？**
> `return` 返回后函数立即结束，无法执行关闭逻辑。`yield` 会暂停函数，请求处理完之后继续执行 `finally` 块，保证 Session 一定被关闭。

**Q: Pydantic 模型和 SQLAlchemy 模型为什么要分开？**
> 职责不同。数据库模型描述表结构（如何存）；Pydantic 模型描述 API 数据（如何校验和返回）。比如密码存数据库但不能返回给前端，id 由数据库生成不需要前端传，两者分开才能灵活控制。

**Q: db.refresh(obj) 是用来做什么的？**
> `commit` 之后从数据库重新读取对象的最新状态，主要用于获取数据库自动生成的字段，比如自增 `id`。不 `refresh` 的话 `id` 会是 None。

---

## Day 5 — JWT 认证

**Q: JWT 的组成结构是什么？payload 里能存什么？**
> JWT 由头部、payload、签名三段组成，用 `.` 分隔。payload 是明文，可存用户 id、用户名、角色等非敏感信息。不能存密码——因为任何人都能解码 payload。

**Q: JWT 是加密还是签名？有什么区别？**
> 是签名不是加密。payload 是明文，任何人都能解码。SECRET_KEY 的作用是验证签名是否合法——用 KEY 对 payload 重新算签名，和 Token 里的比对，一致则未被篡改。类比：公章验真伪，不是加密文件内容。

**Q: Token 失效了怎么处理？**
> Token 过期后接口返回 401，前端检测到 401 跳转登录页让用户重新登录。进阶方案是双 Token 机制：`access_token`（短期）+ `refresh_token`（长期），用 `refresh_token` 自动续期 `access_token`。

**Q: 路由顺序会影响匹配结果吗？**
> 会！FastAPI 按顺序匹配路由，具体路径必须放在动态路径前面：
```python
# 正确：/me 在 /{user_id} 前面
@router.get("/me")
@router.get("/{user_id}")

# 错误：/me 会被当成 user_id 解析，报 422
```

**Q: SECRET_KEY 为什么不能硬编码？**
> 代码上传 GitHub 后所有人都能看到 KEY，攻击者可以伪造任意 Token。正确做法是存环境变量：
```python
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key")
```

---

## Day 6 — 异步与后台任务

**Q: 什么场景下 async def 不会带来性能提升？**
> CPU 密集型任务，如图像处理、大量数学计算、数据加密。这类任务没有 IO 等待，async 无法让出控制权，和同步没有区别。CPU 密集任务应该用多进程（multiprocessing）来解决。

**Q: async def 里能直接调用 time.sleep() 吗？为什么？**
> 不能！`time.sleep()` 是同步阻塞函数，在 `async def` 里调用会堵死整个事件循环，所有请求都无法处理。应该用 `await asyncio.sleep()` 代替。

**Q: BackgroundTasks 和 Celery 有什么区别？**

| | BackgroundTasks | Celery |
|---|---|---|
| 适合场景 | 简单后台任务，开发测试 | 生产环境，高可靠性 |
| 任务丢失 | 服务器重启后任务丢失 | 任务持久化，不丢失 |
| 依赖 | FastAPI 内置 | 需要 Redis/RabbitMQ |

**Q: FastAPI 的异步和 Node.js 的异步有什么相似之处？**
> 两者都基于事件循环（Event Loop）的单线程异步模型，IO 等待时让出控制权处理其他请求，而不是开多线程阻塞等待。都适合 IO 密集型高并发场景。

---

## Day 7 — 测试与部署

**Q: TestClient 的原理是什么？测试时需要启动服务器吗？**
> TestClient 把 FastAPI app 包起来，模拟一个假浏览器直接调用接口处理函数，不需要真正启动 uvicorn 服务器。测试速度极快，适合 CI/CD 自动化流水线。

**Q: assert 在测试里是什么意思？**
> 断言某个条件必须为真，不满足就报错测试失败。`assert res.status_code == 200` 表示"如果状态码不是 200，这个测试用例失败"。

**Q: Dockerfile 里为什么先 COPY requirements.txt 再 COPY . ？**
> 利用 Docker 的层缓存机制。依赖文件不经常变，代码经常变。先安装依赖，只要依赖没变这一层直接用缓存，不重新安装，大幅提升构建速度。

**Q: FastAPI 项目上线前要做哪些配置？**
> 关闭自动文档（`docs_url=None`）、SECRET_KEY 存环境变量、配置 CORS 跨域、使用生产数据库（PostgreSQL）、关闭 `--reload`、设置合适的 workers 数量。

**Q: 如何做接口版本管理？**
```python
router_v1 = APIRouter(prefix="/api/v1/users")
router_v2 = APIRouter(prefix="/api/v2/users")
# 新版本单独建路由文件，老版本继续维护，互不影响
```