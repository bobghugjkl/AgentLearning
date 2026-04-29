from fastapi import FastAPI
from schemas import  Item,UserCreate
from routers import users
from database import engine
from models import Base
import asyncio
import time
from fastapi import FastAPI, BackgroundTasks

Base.metadata.create_all(bind=engine)
app = FastAPI()
@app.get("/sync")
def sync_route():
    time.sleep(2)
    return {"done": "sync"}
@app.get("/async")
async def async_route():
    await asyncio.sleep(2)   # 异步等待，不阻塞
    return {"done": "async"}

def send_email(to: str, content: str):
    time.sleep(3)  # 模拟发邮件耗时
    print(f"邮件已发送给 {to}：{content}")

@app.post("/register")
async def register(email: str, bg: BackgroundTasks):
    bg.add_task(send_email, email, "欢迎注册！")
    return {"status": "注册成功，欢迎邮件发送中..."}
# 第一天
# @app.get("/")
# def hello():
#     return {"message": "Hello FastAPI"}
#
# @app.get("/items/{item_id}")
# def get_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "query": q}
#
# @app.get("/users/{username}")
# def get_username(username: str, age: int = None):
#     return {"username": username, "age": age}
# 第二天
# @app.post("/items/")
# def create_item(item: Item):
#     return {"recived": item.model_dump()}
#
# @app.post("/users/")
# def create_user(user: User):
#     return {"recived": user.model_dump()}
# 第三天
app.include_router(users.router)