FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY .env .env

EXPOSE 8000

ENV DATABASE_URL=${DATABASE_URL}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD [ "uvicorn", "main:app", "--reload" ]
