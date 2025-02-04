from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, select
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import UTC, datetime
import os
import random
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 初始化 FastAPI
app = FastAPI()

# 啟用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定 logging
logging.basicConfig(level=logging.INFO)

# 載入環境變數
load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/acpay_db")

# 設定資料庫連線
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# 定義 ORM 模型
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    prime = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

# 取得 DB 會話
def get_db():
    with SessionLocal() as db:
        yield db

# Pydantic 模型
class OrderCreate(BaseModel):
    email: EmailStr

class PaymentResponse(BaseModel):
    id: int
    email: str
    prime: str
    created_at: datetime

# 模擬 OTP 儲存 (正式環境應使用 Redis 或 DB)
otp_store = {}

@app.get("/")
def root():
    return {"message": "FastAPI 付款管理系統運行中"}

@app.post("/otp")
def generate_otp(email: EmailStr):
    otp_store[email] = random.randint(100000, 999999)
    logging.info(f"OTP for {email}: {otp_store[email]}")  # 實際應寄送 OTP
    return {"message": "OTP 已發送"}

@app.post("/order")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if order.email not in otp_store:
        raise HTTPException(status_code=400, detail="請先驗證 OTP")
    
    otp_store.pop(order.email)  # OTP 只能使用一次
    prime_token = f"test_prime_{random.randint(100000, 999999)}"
    
    payment = Payment(email=order.email, prime=prime_token)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {"order_id": payment.id, "prime": prime_token}

@app.get("/payments", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    stmt = select(Payment).order_by(Payment.created_at.desc())
    return db.execute(stmt).scalars().all()

@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="付款記錄不存在")
    
    db.delete(payment)
    db.commit()
    return {"message": "刪除成功"}
