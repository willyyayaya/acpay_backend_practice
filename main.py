from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import TIMESTAMP, create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

if not API_SECRET_KEY:
    raise ValueError("API_SECRET_KEY 未設定，請在 .env 檔案內設定")

# DATABASE_URL = "mysql+pymysql://admin:admin@mysql:3306/acpay_db"
DATABASE_URL = "mysql+pymysql://admin:admin@localhost:3306/acpay_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=True)
    prime = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 測試
@app.get("/")
def read_root():
    return {"message": "FastAPI is running"}

@app.post("/payments/")
def create_payment(payment_data: dict, db: Session = Depends(get_db)):
    if "<" in payment_data.get("email", ""):
        raise HTTPException(status_code=400, detail="Email 不能包含 HTML 標籤")

    new_payment = Payment(email=payment_data["email"], prime=payment_data["prime"])
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return {"message": "交易創建成功", "order_id": new_payment.id}

@app.get("/payments/")
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()

@app.get("/payments/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄不存在")
    return {"id": payment.id, "email": payment.email}

@app.patch("/payments/{payment_id}")
def update_payment(payment_id: int, payment_data: dict, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄不存在")

    if "email" in payment_data:
        payment.email = payment_data["email"]

    db.commit()
    db.refresh(payment)
    return {"message": "交易記錄更新成功"}

@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="交易記錄不存在")

    db.delete(payment)
    db.commit()
    return {"message": "交易記錄刪除成功"}
