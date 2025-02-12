from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# ✅ 修正 lifespan 問題
@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # 讓應用繼續運行
    await engine.dispose()  # 應用關閉時釋放資料庫連線

app = FastAPI(lifespan=lifespan_handler)

# ✅ 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 修正 MySQL 連線字串
DATABASE_URL = "mysql+aiomysql://admin:admin@localhost:3307/acpay_db"

# ✅ 修正 Async 資料庫設置
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# ✅ 修正 `sessionmaker`，確保是 `async`
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# ✅ 修正 PaymentRecord 定義
class PaymentRecord(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255))
    prime = Column(String(255))

# ✅ 修正 `get_db()`，確保 `async`
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ✅ 修正 Pydantic 模型
class OrderRequest(BaseModel):
    email: EmailStr

class UpdatePaymentRequest(BaseModel):
    email: EmailStr

# ✅ 修正 API: 創建交易記錄
@app.post("/order")
async def create_order(order: OrderRequest, db: AsyncSession = Depends(get_db)):
    import uuid
    prime = str(uuid.uuid4())[:12]  # 模擬 prime 產生
    new_payment = PaymentRecord(email=order.email, prime=prime)

    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    return {"order_id": new_payment.id, "prime": new_payment.prime}

# ✅ 修正 API: 取得所有交易記錄
@app.get("/payments")
async def get_all_payments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PaymentRecord))  # ✅ 正確的查詢方式
    payments = result.scalars().all()
    return payments

# ✅ 修正 API: 更新交易記錄
@app.patch("/payments/{payment_id}")
async def update_payment(payment_id: int, update_request: UpdatePaymentRequest, db: AsyncSession = Depends(get_db)):
    payment = await db.get(PaymentRecord, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄未找到")
    
    payment.email = update_request.email
    await db.commit()
    await db.refresh(payment)
    return {"message": f"交易記錄 {payment_id} 已更新", "updated_email": payment.email}

# ✅ 修正 API: 刪除交易記錄
@app.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    payment = await db.get(PaymentRecord, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄未找到")

    await db.delete(payment)
    await db.commit()
    return {"message": f"交易記錄 {payment_id} 已刪除"}
