# 使用 Python 官方映像檔
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製應用程式代碼
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 允許 Docker 直接執行應用程式
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
