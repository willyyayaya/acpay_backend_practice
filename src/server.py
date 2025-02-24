import os
import subprocess
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from requests import Session
from sqlalchemy import TIMESTAMP, create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from starlette.requests import Request

from src.dependencies.auth import get_admin_user
from src.dependencies.basic import get_db
from src.routers.server import router
from src.schemas.basic import TextOnly
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FastAPI Backend Practice",
    description="Template Description",
    version="0.0.1",
    contact={
        "name": "Author Name",
        "email": "example@exmaple.com",
    },
    swagger_ui_parameters={'docExpansion': 'none'}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=True)
    prime = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
@app.get("/", response_model=TextOnly)
async def root():
    return TextOnly(text="Hello World")


@app.get("/elements", include_in_schema=False)
async def api_documentation(request: Request):
    return HTMLResponse("""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Elements in HTML</title>

    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
  </head>
  <body>

    <elements-api
      apiDescriptionUrl="openapi.json"
      router="hash"
    />

  </body>
</html>""")


if os.getenv('DEV', 'false') == 'true':
    @app.post("/renewDB", dependencies=[Depends(get_admin_user)])
    async def renew_database():
        from src.database.database import TRIAL_URL, DB_NAME, engine, drop_all_tables
        from src.database.database import create_all_tables, create_database_if_not_exists
        from src.database.utils import add_test_data

        create_database_if_not_exists(TRIAL_URL, DB_NAME)
        drop_all_tables(engine)
        create_all_tables(engine)
        add_test_data()
        return TextOnly(text="Database Renewed")


@app.post('/alembic', dependencies=[Depends(get_admin_user)])
async def alembic(
        db: Annotated[Session, Depends(get_db)]
):
    # remove alembic_version table
    db.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.commit()

    # execute `bash /run/run_alembic.sh` and return the output
    process = subprocess.Popen(['/bin/bash', '/run/run_alembic.sh'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = process.communicate()

    return {
        "output": output.decode('utf-8').split('\n'),
        "error": error.decode('utf-8').split('\n')
    }

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