# 🛒 Smart Retail AI System (智慧零售 AI 微服務)
這是一個企業級的智慧零售解決方案，整合了 FastAPI、Docker、PostgreSQL (pgvector) 以及先進的 AI 模型。系統分為兩大核心模組：RAG 智慧客服知識庫（支援語意混合搜尋）與 AI 銷量預測（感應節慶趨勢）。

## 🌟 功能亮點 (Key Features)
### 1. 🧠 RAG 智慧知識庫 (AI Chatbot Backend)
- 混合語意搜尋 (Hybrid Search)：結合向量空間搜尋與結構化權重加權（Boosting），大幅提升查詢精準度。
- 權重優化邏輯：針對 標題 (Title)、分類 (Category) 與 標籤 (Tags) 進行動態評分加成，解決純向量搜尋無法精確識別特定實體（如 Foodpanda）的問題。
- Markdown CMS：整合 uiw/react-md-editor，支援圖片直接貼上、自動預覽與 Markdown 渲染。
- 向量化存儲：使用 paraphrase-multilingual-MiniLM-L12-v2 (384 維) 並存儲於 PostgreSQL 的 pgvector。

### 2. 📈 銷量預測與趨勢分析 (Sales Forecasting)
- Prophet AI 模型：使用 Meta Prophet 進行時間序列預測，自動偵測季節性規律。
- 節慶權重感應 (Holiday Awareness)：內建台灣國定假日（如農曆新年、228 連假）影響因子，能自動預測節慶期間的銷量波動。
- 四階段引導 UI：從 CSV 上傳、模型訓練、參數設定到結果預測，提供流暢的使用者體驗。

## 🛠️ 技術棧 (Tech Stack)
**後端 (Backend)**
- Framework: FastAPI (Python 3.10)
- Database: PostgreSQL 16 + pgvector
- AI Engine:
    - prophet (Time Series Analysis)
    - sentence-transformers (NLP Embedding)
    - joblib (Model Persistence)

**前端 (Frontend)**
- Framework: React 18 (Vite)
- UI Library: Mantine UI, Tabler Icons
- Editor: @uiw/react-md-editor

## 📂 專案結構 (Project Structure)
```
Root
.
├── backend-ai/
│   ├── main.py              # FastAPI 主程式 (包含 RAG & Sales API)
│   ├── models/              # 存放訓練好的 .pkl 模型
│   ├── static/uploads/      # 知識庫圖片上傳目錄
│   └── requirements.txt     # Python 依賴
├── frontend/
│   ├── src/
│   │   ├── components/      # 拆分後的頁面元件 (Search, Manage, Config, Sales)
│   │   ├── App.jsx          # 全域狀態管理與路由
│   │   └── api.js           # API 網址設定
├── db-data/
│   └── init.sql             # 資料庫初始化腳本 (含 HNSW 索引優化)
└── docker-compose.yml       # 一鍵啟動設定
```

## 🚀 快速開始 (Quick Start)

### 1. 啟動全系統
```
docker-compose up -d --build
```

### 2. 準備測試數據
- 銷量數據：執行 generate_mock_sales.py 產生 CSV，並透過網頁「銷量預測」分頁上傳。

### 3. 開啟介面
- 前端網頁：http://localhost:5173
- API 文件：http://localhost:8000/docs