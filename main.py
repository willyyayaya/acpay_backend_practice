from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

DATABASE_URL = "mysql+aiomysql://admin:admin@mysql:3306/acpay_db"

# 初始化資料庫連接
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定義一個測試資料表
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

# 創建 FastAPI 應用
app = FastAPI()

# 測試資料庫連線
@app.get("/ping-db")
async def ping_db():
    async with SessionLocal() as session:
        try:
            result = await session.execute("SELECT 1")
            return {"status": "success", "message": "Database connected"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# 啟動時自動建立資料表
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
