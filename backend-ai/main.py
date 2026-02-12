import os
import shutil
import uuid
import joblib
import pandas as pd

from prophet import Prophet
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Smart Retail Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.router.redirect_slashes = False

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

os.makedirs("models", exist_ok=True)

DB_URL = os.getenv('DATABASE_URL', 'postgresql://admin:000@db:5432/retail_ops')
engine = create_engine(DB_URL)

print("正在載入 Embedding 模型...")
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ==========================================
# DTO
# ==========================================
class DocumentInput(BaseModel):
    title: str
    category: str
    outline: str
    content: str
    tags: List[str] = []

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    search_type: str = "smart"
    category_filter: Optional[str] = None

class FeedbackRequest(BaseModel):
    action: str # "helpful" or "unhelpful"

class StringItem(BaseModel):
    name: str

# ==========================================
# API 實作
# ==========================================

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"url": f"/static/uploads/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [Create] 新增文件
@app.post("/documents/create")
def create_document(doc: DocumentInput):
    text_to_embed = f"{doc.title} {doc.title} {doc.category} {doc.outline}"
    embedding_vector = embedding_model.encode(text_to_embed, normalize_embeddings=True).tolist()

    with engine.begin() as conn:
        # A. 寫入文件
        insert_sql = text("""
            INSERT INTO documents (title, category, outline, content, embedding)
            VALUES (:title, :category, :outline, :content, :embedding)
            RETURNING id
        """)
        result = conn.execute(insert_sql, {
            "title": doc.title, "category": doc.category, "outline": doc.outline, 
            "content": doc.content, "embedding": str(embedding_vector)
        })
        new_doc_id = result.fetchone()[0]

        # B. 處理標籤
        update_tags(conn, new_doc_id, doc.tags)

    return {"status": "success", "doc_id": new_doc_id}

# [Update] 更新文件
@app.put("/documents/{doc_id}")
def update_document(doc_id: int, doc: DocumentInput):
    text_to_embed = f"{doc.title} {doc.title} {doc.category} {doc.outline}"
    embedding_vector = embedding_model.encode(text_to_embed, normalize_embeddings=True).tolist()

    with engine.begin() as conn:
        # 1. 更新主表
        update_sql = text("""
            UPDATE documents 
            SET title=:title, category=:category, outline=:outline, content=:content, embedding=:embedding
            WHERE id=:id
        """)
        result = conn.execute(update_sql, {
            "title": doc.title, "category": doc.category, "outline": doc.outline, 
            "content": doc.content, "embedding": str(embedding_vector), "id": doc_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Document not found")

        # 2. 重建標籤關聯 (先刪除舊關聯，再新增新關聯)
        conn.execute(text("DELETE FROM document_tags WHERE document_id = :id"), {"id": doc_id})
        update_tags(conn, doc_id, doc.tags)

    return {"status": "success", "message": "已更新"}

# [Delete] 刪除文件
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    with engine.begin() as conn:
        result = conn.execute(text("DELETE FROM documents WHERE id = :id"), {"id": doc_id})
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "message": "已刪除"}

# [Feedback] 評價 (有幫助/沒幫助)
@app.post("/documents/{doc_id}/feedback")
def feedback_document(doc_id: int, req: FeedbackRequest):
    col = "helpful_count" if req.action == "helpful" else "unhelpful_count"
    sql = text(f"UPDATE documents SET {col} = {col} + 1 WHERE id = :id")
    
    with engine.begin() as conn:
        conn.execute(sql, {"id": doc_id})
    return {"status": "success"}

# [Helper] 標籤處理函式
def update_tags(conn, doc_id, tags_list):
    for tag_name in tags_list:
        # 確保 Tag 存在
        conn.execute(text("""
            INSERT INTO tags (name, usage_count) VALUES (:name, 1)
            ON CONFLICT (name) DO UPDATE SET usage_count = tags.usage_count + 1
        """), {"name": tag_name})
        
        tag_id = conn.execute(text("SELECT id FROM tags WHERE name = :name"), {"name": tag_name}).scalar()
        
        # 建立關聯
        conn.execute(text("""
            INSERT INTO document_tags (document_id, tag_id) VALUES (:doc_id, :tag_id)
            ON CONFLICT DO NOTHING
        """), {"doc_id": doc_id, "tag_id": tag_id})

# [Search] 搜尋 (更新：需回傳 tags 和 unhelpful_count)
@app.post("/search")
def search_documents(req: SearchRequest):
    results = []
    params = {
        "query": req.query, 
        "exact_query": f"%{req.query}%", 
        "top_k": req.top_k
    }

    # 1. 基礎條件與過濾
    cat_filter_clause = ""
    if req.category_filter and req.category_filter != "全部":
        cat_filter_clause = "AND d.category = :cat_filter"
        params["cat_filter"] = req.category_filter

    # 2. 根據 search_type 決定 SQL
    if req.search_type == "exact":
        # === [精準模式] 只看標題匹配，按 ID 排序 ===
        sql = text(f"""
            SELECT d.id, d.title, d.category, d.outline, d.content, d.helpful_count, d.unhelpful_count,
                   1.0 AS score,
                   COALESCE(ARRAY_AGG(t.name) FILTER (WHERE t.name IS NOT NULL), '{{}}') as tags
            FROM documents d
            LEFT JOIN document_tags dt ON d.id = dt.document_id
            LEFT JOIN tags t ON dt.tag_id = t.id
            WHERE d.title ILIKE :exact_query {cat_filter_clause}
            GROUP BY d.id
            ORDER BY d.id DESC
            LIMIT :top_k
        """)
    else:
        # === [智能模式] 語義搜尋 + 分類/標題加分 ===
        query_vec = embedding_model.encode(req.query, normalize_embeddings=True).tolist()
        params["query_vec"] = str(query_vec)
        
        sql = text(f"""
            SELECT d.id, d.title, d.category, d.outline, d.content, d.helpful_count, d.unhelpful_count,
                   LEAST(
                        (1 - (d.embedding <=> :query_vec)) + 
                        (CASE WHEN d.category ILIKE :query THEN 0.3 ELSE 0 END) + 
                        (CASE WHEN d.title ILIKE :exact_query THEN 0.1 ELSE 0 END),
                        1.0
                    ) AS score,
                   COALESCE(ARRAY_AGG(t.name) FILTER (WHERE t.name IS NOT NULL), '{{}}') as tags
            FROM documents d
            LEFT JOIN document_tags dt ON d.id = dt.document_id
            LEFT JOIN tags t ON dt.tag_id = t.id
            WHERE 1=1 {cat_filter_clause}
            GROUP BY d.id, d.title, d.category, d.outline, d.content, d.helpful_count, d.unhelpful_count, d.embedding
            ORDER BY score DESC
            LIMIT :top_k
        """)

    with engine.connect() as conn:
        rows = conn.execute(sql, params).fetchall()
        for row in rows:
            results.append({
                "id": row.id,
                "title": row.title,
                "category": row.category,
                "outline": row.outline,
                "content": row.content,
                "score": round(row.score, 4),
                "helpful_count": row.helpful_count,
                "unhelpful_count": row.unhelpful_count or 0,
                "tags": row.tags
            })

    return {"query": req.query, "results": results}

@app.get("/config/all")
def get_config():
    with engine.connect() as conn:
        cats = conn.execute(text("SELECT name FROM categories ORDER BY name")).fetchall()
        tags = conn.execute(text("SELECT name FROM tags ORDER BY usage_count DESC")).fetchall()
    return {"categories": [r[0] for r in cats], "tags": [r[0] for r in tags]}

@app.post("/config/categories")
def add_category(item: StringItem):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO categories (name) VALUES (:name)"), {"name": item.name})
    return {"status": "success"}

@app.delete("/config/categories/{name}")
def delete_category(name: str):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM categories WHERE name = :name"), {"name": name})
    return {"status": "success"}

@app.post("/config/tags")
def add_tag(item: StringItem):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO tags (name, usage_count) VALUES (:name, 0)"), {"name": item.name})
    return {"status": "success"}

@app.delete("/config/tags/{name}")
def delete_tag(name: str):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM tags WHERE name = :name"), {"name": name})
    return {"status": "success"}

# 定義請求格式 (這就是 DTO)
class PredictionRequest(BaseModel):
    product_id: str
    days: int = 7  # 預設預測未來 7 天

# ==========================================
# [API 5] 銷量預測模組 (Sales Prediction)
# ==========================================

# 步驟 1: 上傳 CSV 並寫入資料庫
@app.post("/sales/upload")
async def upload_sales_data(file: UploadFile = File(...)):
    try:
        # 讀取 CSV
        df = pd.read_csv(file.file)
        
        # 簡單驗證欄位
        required_cols = {'product_id', 'transaction_date', 'quantity'}
        if not required_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"CSV 格式錯誤，需包含: {required_cols}")

        # 寫入資料庫 (使用 pandas 的 to_sql 雖然慢一點但最方便，這裡改用 SQL 確保與 SQLAlchemy 相容)
        # 為了效能，我們用 Transaction 批量插入
        with engine.begin() as conn:
            # 先清空舊資料 (看你的需求，這裡假設是重新匯入)
            conn.execute(text("TRUNCATE TABLE sales_data RESTART IDENTITY"))
            
            # 轉換為 dict list 插入
            data_to_insert = df.to_dict(orient='records')
            conn.execute(
                text("""
                    INSERT INTO sales_data (product_id, transaction_date, quantity)
                    VALUES (:product_id, :transaction_date, :quantity)
                """),
                data_to_insert
            )
            
        return {"status": "success", "count": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 步驟 2: 訓練模型
@app.post("/sales/train")
def train_model():
    try:
        # 1. 從 DB 撈資料
        sql = "SELECT transaction_date as ds, quantity as y FROM sales_data ORDER BY transaction_date"
        df = pd.read_sql(sql, engine)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="資料庫無數據，請先上傳 CSV")

        # 2. 初始化 Prophet 模型
        m = Prophet()
        m.add_country_holidays(country_name='TW')
        m.fit(df)
        
        # 3. 儲存模型
        model_path = "models/sales_model.pkl"
        joblib.dump(m, model_path)
        
        return {"status": "success", "message": "模型訓練完成並已儲存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 步驟 3 & 4: 預測
class PredictRequest(BaseModel):
    days: int

@app.post("/sales/predict")
def predict_sales(req: PredictRequest):
    model_path = "models/sales_model.pkl"
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="模型尚未訓練，請先執行訓練步驟")
        
    try:
        # 1. 載入模型
        m = joblib.load(model_path)
        
        # 2. 建立未來日期
        future = m.make_future_dataframe(periods=req.days)
        
        # 3. 預測
        forecast = m.predict(future)
        
        # 4. 取出結果 (只取未來的資料)
        result = forecast[['ds', 'yhat']].tail(req.days)
        
        # 格式化回傳
        data = []
        for _, row in result.iterrows():
            data.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "predicted_sales": int(row['yhat']) # 轉整數比較好看
            })
            
        return {"results": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))