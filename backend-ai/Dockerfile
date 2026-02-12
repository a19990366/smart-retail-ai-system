# 使用官方輕量級 Python 3.10 (Linux Debian 版本)
FROM python:3.10-slim

# 設定容器內的工作目錄
WORKDIR /app

# 安裝系統層級依賴 (Prophet 和 PostgreSQL Driver 需要這些 C++ 編譯工具)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .

# ==========================================
# [關鍵] 強制安裝 CPU 版 PyTorch，拒絕 NVIDIA 顯卡驅動
# ==========================================
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 這裡再安裝剩下的，因為 torch 已經裝好了，它會自動跳過 gpu 版
RUN pip install --no-cache-dir -r requirements.txt

# 複製剩下的程式碼 (main.py, train.py 等)
COPY . .

# 預設啟動指令：啟動 FastAPI
# --host 0.0.0.0 是關鍵，這樣 Docker 外部才能連進來
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]