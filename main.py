from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
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
DB_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:@localhost/acpay_db")

# 設定異步資料庫連線
engine = create_async_engine(DB_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# 定義 ORM 模型
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    prime = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# 取得 DB 會話
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Pydantic 模型
class OrderCreate(BaseModel):
    email: EmailStr

class PaymentUpdate(BaseModel):
    email: EmailStr | None = None  # 支援部分更新

class PaymentResponse(BaseModel):
    id: int
    email: str
    prime: str
    created_at: datetime

# 模擬 OTP 儲存（正式環境應使用 Redis 或 DB）
otp_store = {}

@app.get("/")
async def root():
    return {"message": "FastAPI 付款管理系統運行中"}

# 建立訂單（僅生成 prime，前端需自行完成付款）
@app.post("/order", response_model=dict)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    prime_token = f"test_prime_{random.randint(100000, 999999)}"
    new_payment = Payment(email=order.email, prime=prime_token)
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    
    return {"order_id": new_payment.id, "prime": prime_token}

# 取得所有交易記錄
@app.get("/payments", response_model=list[PaymentResponse])
async def get_payments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).order_by(Payment.created_at.desc()))
    return result.scalars().all()

# 刪除交易記錄
@app.delete("/payments/{payment_id}", response_model=dict)
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).filter_by(id=payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="付款記錄不存在")

    await db.delete(payment)
    await db.commit()
    
    return {"message": "刪除成功"}

# 更新交易記錄（支持 PATCH，部分更新）
@app.patch("/payments/{payment_id}", response_model=dict)
async def update_payment(payment_id: int, payment_update: PaymentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).filter_by(id=payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="付款記錄不存在")

    if payment_update.email:
        payment.email = payment_update.email

    await db.commit()
    await db.refresh(payment)
    
    return {"message": "更新成功", "payment": {"id": payment.id, "email": payment.email, "prime": payment.prime, "created_at": payment.created_at}}
