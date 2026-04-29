from fastapi import APIRouter, Depends
from schemas import UserCreate
from sqlalchemy.orm import Session
from database import get_db
from models import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import create_token, verify_token

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # token 就是从请求头里自动提取出来的字符串
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效Token")
    return payload["sub"]

def common_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

@router.put("/{user_id}")
def update_user(user_id:int, user:UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return {"message": "User does not exist"}
    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return {"message": "User does not exist"}
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

@router.post("/login")
def login(username: str, password: str):
    # 模拟验证，实际项目里要查数据库
    if username == "admin" and password == "123":
        token = create_token({"sub": username})
        return {"token": token}
    raise HTTPException(status_code=401, detail="用户名或密码错误")

