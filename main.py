from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
import pymysql
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 載入環境變數
load_dotenv()

# MySQL 連線設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "acpay_db")

# 建立 FastAPI 應用程式
app = FastAPI()

# 設定 CORS，允許前端存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以改成你的前端網址，例如 http://127.0.0.1:5500
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 資料模型
class PaymentCreate(BaseModel):
    email: str
    prime: str

class PaymentUpdate(BaseModel):
    email: str

class PaymentResponse(BaseModel):
    id: int
    email: str
    prime: str
    created_at: datetime  # 使用 datetime 來表示時間戳
    
# 資料庫連線函式
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# 根目錄測試
@app.get("/")
async def root():
    return {"message": "FastAPI 付款管理系統運行中"}

# 創建支付記錄 (Create)
@app.post("/checkout", response_model=dict)
async def create_payment(payment: PaymentCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO payments (email, prime) VALUES (%s, %s)"
            cursor.execute(sql, (payment.email, payment.prime))
            connection.commit()
            return {"message": "付款成功!", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料庫錯誤: {str(e)}")
    finally:
        connection.close()

# 取得所有支付記錄 (Read)
@app.get("/payments", response_model=List[PaymentResponse])
async def get_payments():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, email, prime, created_at FROM payments ORDER BY created_at DESC"
            cursor.execute(sql)
            payments = cursor.fetchall()
            return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料庫查詢失敗: {str(e)}")
    finally:
        connection.close()

# 更新支付記錄 (Update)
@app.put("/payments/{payment_id}", response_model=dict)
async def update_payment(payment_id: int, payment: PaymentUpdate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE payments SET email = %s WHERE id = %s"
            cursor.execute(sql, (payment.email, payment_id))
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="找不到該筆付款記錄")
            return {"message": "更新成功!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失敗: {str(e)}")
    finally:
        connection.close()

# 刪除支付記錄 (Delete)
@app.delete("/payments/{payment_id}", response_model=dict)
async def delete_payment(payment_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM payments WHERE id = %s"
            cursor.execute(sql, (payment_id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="找不到該筆付款記錄")
            return {"message": "刪除成功!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除失敗: {str(e)}")
    finally:
        connection.close()
