# FastAPI Day 4 — 数据库集成（SQLAlchemy + SQLite）

## 1. 为什么用 ORM（SQLAlchemy）

- 不用写 SQL 字符串，直接用 Python 对象操作数据库
- 换数据库只改一行连接配置（SQLite → MySQL → PostgreSQL）
- 自动防止 SQL 注入

---

## 2. 项目结构

```
fastapi-learn/
├── main.py
├── database.py    ← 数据库连接配置
├── models.py      ← 数据库表定义
├── schemas.py     ← Pydantic 数据模型
└── routers/
    └── users.py
```

---

## 3. database.py — 数据库连接

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./tests.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db       # 请求使用 Session
    finally:
        db.close()     # 请求结束自动关闭
```

- `engine` — 数据库连接器
- `SessionLocal` — Session 工厂，每次调用生产一个新 Session
- `Base` — 所有数据库模型的基类
- `get_db` — 配合 `Depends` 使用，每次请求自动创建/关闭 Session
- `yield` vs `return`：yield 返回后函数暂停，请求结束后继续执行 finally 关闭逻辑

---

## 4. models.py — 数据库表定义

```python
from sqlalchemy import Column, Integer, String
from database import Base, engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

Base.metadata.create_all(bind=engine)  # 启动时自动建表
```

---

## 5. Pydantic 模型 vs 数据库模型

| | Pydantic 模型（schemas.py） | 数据库模型（models.py） |
|---|---|---|
| 作用 | 校验 API 接收/返回的数据 | 描述数据库表结构 |
| 继承 | `BaseModel` | `Base` |
| 场景 | 前端发来的 JSON | 存到数据库的数据 |

**为什么分开？** 接口层和数据库层职责不同——比如密码存数据库但不能返回给前端，`id` 由数据库生成不需要前端传。

```python
# schemas.py — API 层
class UserCreate(BaseModel):
    username: str = Field(min_length=2)
    email: str
```

---

## 6. 完整 CRUD 接口

```python
# routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate

router = APIRouter(prefix="/users", tags=["users"])

# 创建
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)   # 获取数据库生成的 id 等字段
    return db_user

# 查询全部
@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# 查询单个
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

# 更新
@router.put("/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return {"message": "User does not exist"}
    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

# 删除
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return {"message": "User does not exist"}
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
```

---

## 7. CRUD 操作对照表

| 操作 | HTTP 方法 | 路径 | 核心代码 |
|------|-----------|------|----------|
| 创建 | POST | `/users/` | `db.add()` + `db.commit()` |
| 查询全部 | GET | `/users/` | `db.query(User).all()` |
| 查询单个 | GET | `/users/{id}` | `.filter().first()` |
| 更新 | PUT | `/users/{id}` | 修改字段 + `db.commit()` |
| 删除 | DELETE | `/users/{id}` | `db.delete()` + `db.commit()` |

---

## 8. 易错点

- `db.refresh(obj)` — commit 之后必须 refresh 才能拿到数据库生成的 id
- `yield` 写法确保 Session 请求后一定关闭，不能用 `return`
- Pydantic 模型和数据库模型**必须分开定义**，职责不同

---

## 9. 面试常见问题

**Q: FastAPI 中如何管理数据库 Session 的生命周期？**
> 用 `yield` 写法的 `get_db` 函数配合 `Depends`，每次请求自动创建 Session，请求结束后 finally 块自动关闭，确保不泄漏连接。

**Q: 为什么 get_db 用 yield 而不是 return？**
> `return` 返回后函数立即结束，无法执行关闭逻辑。`yield` 会在请求处理完之后继续执行 `finally` 块，保证 Session 一定被关闭。