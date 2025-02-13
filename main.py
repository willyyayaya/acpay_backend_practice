from aiomysql import OperationalError
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
import uuid
import asyncio

# 設定 CORS
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL 連接設定
DATABASE_URL = "mysql+aiomysql://admin:admin@mysql:3307/acpay_db"

# 創建 MySQL 非同步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# 使用 sessionmaker 來創建資料庫會話
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# 定義資料模型
class PaymentRecord(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255))
    prime = Column(String(255))

# 等待 MySQL 準備好
async def wait_for_db():
    retries = 10
    while retries > 0:
        try:
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            print("✅ MySQL 連線成功！")
            return
        except OperationalError:
            print("⏳ MySQL 尚未準備好，5 秒後重試...")
            retries -= 1
            await asyncio.sleep(5)

    print("❌ MySQL 連線失敗，請檢查設定！")

# 用於應用啟動和關閉
@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await wait_for_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan_handler)

# 資料庫會話取得
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Pydantic 模型
class OrderRequest(BaseModel):
    email: EmailStr

class UpdatePaymentRequest(BaseModel):
    email: EmailStr

# 創建交易記錄
@app.post("/order")
async def create_order(order: OrderRequest, db: AsyncSession = Depends(get_db)):
    prime = str(uuid.uuid4())[:12]  # 模擬 prime 產生
    new_payment = PaymentRecord(email=order.email, prime=prime)

    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    return {"order_id": new_payment.id, "prime": new_payment.prime}

# 取得所有交易記錄
@app.get("/payments")
async def get_all_payments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PaymentRecord))
    payments = result.scalars().all()
    return payments

# 更新交易記錄
@app.patch("/payments/{payment_id}")
async def update_payment(payment_id: int, update_request: UpdatePaymentRequest, db: AsyncSession = Depends(get_db)):
    payment = await db.get(PaymentRecord, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄未找到")

    payment.email = update_request.email
    await db.commit()
    await db.refresh(payment)
    return {"message": f"交易記錄 {payment_id} 已更新", "updated_email": payment.email}

# 刪除交易記錄
@app.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    payment = await db.get(PaymentRecord, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄未找到")

    await db.delete(payment)
    await db.commit()
    return {"message": f"交易記錄 {payment_id} 已刪除"}
