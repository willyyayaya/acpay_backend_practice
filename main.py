from fastapi import FastAPI
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

app = FastAPI()

# 資料庫連線設定
DATABASE_URL = "mysql+pymysql://admin:admin@mysql:3306/acpay_db"

# 建立同步 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL)

# 建立 Session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_db_connection():
    """測試 MySQL 連線"""
    try:
        connection = pymysql.connect(
            host="mysql",
            user="admin",
            password="admin",
            database="acpay_db",
            port=3306
        )
        connection.close()
        return True
    except pymysql.MySQLError as e:
        print(f"❌ MySQL 連線失敗: {e}")
        return False

@app.get("/")
def read_root():
    """首頁，測試 API 是否正常運行"""
    return {"message": "FastAPI is running 🚀"}

@app.get("/test-db")
def test_database():
    """測試資料庫連線"""
    if test_db_connection():
        return {"message": "✅ 成功連線到 MySQL"}
    else:
        return {"message": "❌ 無法連線到 MySQL"}

@app.get("/test-sqlalchemy")
def test_sqlalchemy():
    """測試 SQLAlchemy 連線"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return {"message": "✅ SQLAlchemy 成功連線到 MySQL", "result": result.fetchone()}
    except OperationalError as e:
        return {"message": f"❌ SQLAlchemy 連線失敗: {str(e)}"}

