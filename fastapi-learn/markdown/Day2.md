# FastAPI Day 2 — 请求体 + Pydantic 数据校验

## 1. 为什么需要 Pydantic

URL 参数只能传简单数据，前端发 JSON 数据时放在请求体（Body）里：

```json
{"name": "book", "price": 9.9}
```

Pydantic 的作用：**提前声明字段类型，自动校验，出错返回 422，不需要手动写任何校验代码。**

---

## 2. 定义数据模型

```python
# schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    name: str
    price: float = Field(gt=0, description="必须大于0")
    description: Optional[str] = None
```

- `BaseModel` — Pydantic 的基础类，继承它后自动拥有校验能力
- `Optional[str] = None` — 可选字段，不传默认为 None
- `Field(gt=0)` — 添加额外校验规则

---

## 3. 必填 vs 可选的判断规则

| 写法 | 是否必填 |
|------|----------|
| `name: str` | 必填 |
| `name: str = None` | 可选 |
| `name: Optional[str] = None` | 可选 |
| `age: Optional[int] = Field(gt=0, default=None)` | 可选，但传了必须 > 0 |

**规则：有默认值（包括 `= None`）就是可选，没有默认值就是必填。**

---

## 4. 在接口中使用模型

```python
# main.py
from fastapi import FastAPI
from schemas import Item

app = FastAPI()

@app.post("/items/")
def create_item(item: Item):
    return item  # FastAPI 自动把 Pydantic 对象转成 JSON
```

- 用 `@app.post` 接收请求体
- 函数参数类型标注为 `Item`，FastAPI 自动解析并校验

---

## 5. Field 常用参数

```python
Field(gt=0)          # 大于 0
Field(ge=0)          # 大于等于 0
Field(lt=100)        # 小于 100
Field(le=100)        # 小于等于 100
Field(min_length=2)  # 字符串最短 2 位
Field(max_length=50) # 字符串最长 50 位
Field(default=None)  # 默认值
Field(description="说明文字")  # 文档说明
```

---

## 6. model_dump()

把 Pydantic 对象转成普通 Python 字典：

```python
item.model_dump()
# 输出：{"name": "book", "price": 9.9, "description": None}
```

实际开发中直接 `return item` 即可，FastAPI 会自动处理转换。

---

## 7. 练习题（自己完成）

```python
class User(BaseModel):
    username: str = Field(min_length=2)
    age: Optional[int] = Field(gt=0, default=None)
    email: str
```

---

## 8. 面试常见问题

**Q: Pydantic 是用来做什么的？**
> 用来定义数据模型并自动做类型校验。在 FastAPI 中，请求体数据会自动经过 Pydantic 校验，类型不对或缺少必填字段时自动返回 422 错误。

**Q: 422 Unprocessable Entity 是什么情况下触发的？**
> 请求体数据不符合 Pydantic 模型定义时触发，比如：缺少必填字段、字段类型错误、不满足 Field 校验规则（如 gt=0 但传了负数）。

---

## 9. 完整 schemas.py

```python
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    name: str
    price: float = Field(gt=0, description="必须大于0")
    description: Optional[str] = None

class User(BaseModel):
    username: str = Field(min_length=2)
    age: Optional[int] = Field(gt=0, default=None)
    email: str
```