# 🛒 Smart Retail AI System (智慧零售 AI 微服務)

這是一個基於微服務架構的智慧零售系統，整合了 **FastAPI**、**Docker**、**PostgreSQL (pgvector)** 以及 **AI 模型**，實現銷量預測與智慧客服功能。

## 🌟 功能亮點 (Key Features)

* **銷量預測 (Sales Forecasting)**: 使用 Meta Prophet 模型，針對不同商品進行未來 7 天的銷量預測。
* **RAG 智慧客服 (AI Chatbot)**: 整合 `paraphrase-multilingual-MiniLM-L12-v2` 模型與 pgvector，實現基於語意搜尋的知識庫問答。
* **容器化部署 (Dockerized)**: 全系統封裝於 Docker Compose，一鍵啟動。
* **高效能資料庫**: 使用 PostgreSQL 處理關聯式數據與向量數據。

## 🛠️ 技術棧 (Tech Stack)

* **Language**: Python 3.10
* **Framework**: FastAPI, Uvicorn
* **Database**: PostgreSQL 16 (with pgvector extension)
* **AI Models**:
    * Time Series: `prophet`
    * Embedding: `sentence-transformers`
* **DevOps**: Docker, Docker Compose

## 🚀 快速開始 (Quick Start)

### 1. 啟動服務
```bash
docker-compose up -d --build

# 生成假銷售數據
docker-compose exec backend-ai python scripts/generate_fake_data.py

# 訓練銷量預測模型
docker-compose exec backend-ai python train.py

# 注入 RAG 知識庫向量
docker-compose exec backend-ai python ingest.py

# 開啟測試API
http://127.0.0.1:8000/docs