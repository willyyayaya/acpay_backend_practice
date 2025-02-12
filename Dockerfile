# 使用 Python 官方映像檔
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製你的應用程式檔案
COPY . .

# 安裝必要的 Python 依賴
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 複製 .env 文件到容器中
COPY .env .env

# 開放 FastAPI 伺服器的端口
EXPOSE 8000

# 設定環境變數以便 Python 程式讀取 .env
ENV DATABASE_URL=${DATABASE_URL}

# 執行 FastAPI 伺服器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD [ "uvicorn", "main:app", "--reload" ]
