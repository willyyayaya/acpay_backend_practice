from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import pymysql

app = FastAPI()

# 資料庫連線設定
# DATABASE_URL = "mysql+pymysql://admin:admin@mysql:3306/acpay_db"
DATABASE_URL = "mysql+pymysql://admin:admin@localhost:3306/acpay_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """取得資料庫 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection() -> bool:
    """測試 MySQL 連線"""
    try:
        with pymysql.connect(
            host="localhost",
            user="admin",
            password="admin",
            database="acpay_db",
            port=3306
        ) as connection:
            return True
    except pymysql.MySQLError as e:
        print(f"MySQL 連線失敗: {e}")
        return False

@app.get("/")
def read_root():
    """首頁，測試 API 是否正常運行"""
    return {"message": "FastAPI is running "}

@app.get("/test-db")
def test_database():
    """測試 MySQL 連線"""
    return {"message": "成功連線到 MySQL" if test_db_connection() else "無法連線到 MySQL"}

@app.get("/test-sqlalchemy")
def test_sqlalchemy(db: Session = Depends(get_db)):
    """測試 SQLAlchemy 連線"""
    try:
        result = db.execute(text("SELECT 1"))
        return {"message": "SQLAlchemy 成功連線到 MySQL", "result": result.fetchone()}
    except Exception as e:
        return {"message": f"SQLAlchemy 連線失敗: {str(e)}"}
