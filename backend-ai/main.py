from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer

app = FastAPI()

# 定義請求格式 (這就是 DTO)
class PredictionRequest(BaseModel):
    product_id: str
    days: int = 7  # 預設預測未來 7 天

# 全域變數用來快取模型
models = {}

def load_model(product_id: str):
    """
    動態載入模型：如果記憶體沒有，就去硬碟讀取 .pkl
    """
    if product_id in models:
        return models[product_id]
    
    model_path = f"models/{product_id}.pkl"
    if not os.path.exists(model_path):
        return None
    
    print(f"📥 正在載入模型: {model_path}")
    model = joblib.load(model_path)
    models[product_id] = model
    return model

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Core"}

@app.post("/predict")
def predict_sales(request: PredictionRequest):
    # 1. 載入模型
    model = load_model(request.product_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model for {request.product_id} not found. Please train it first.")

    # 2. 建立未來日期 (Prophet 的標準用法)
    future = model.make_future_dataframe(periods=request.days)
    
    # 3. 進行預測
    forecast = model.predict(future)
    
    # 4. 整理回傳結果 (只回傳未來的預測值)
    # 取最後 N 天的資料
    result = forecast[['ds', 'yhat']].tail(request.days)
    
    # 轉成 JSON 格式回傳
    response = []
    for _, row in result.iterrows():
        response.append({
            "date": row['ds'].strftime('%Y-%m-%d'),
            "predicted_sales": round(row['yhat'], 2)
        })
        
    return {
        "product_id": request.product_id,
        "forecast": response
    }

# === 新增：RAG 相關變數 ===
# 初始化 Embedding 模型 (會自動下載或讀取 cache)
rag_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 資料庫連線 (記得加這段)
DB_URL = os.getenv('DATABASE_URL', 'postgresql://admin:000@localhost:5432/retail_ops')
engine = create_engine(DB_URL)

class QuestionRequest(BaseModel):
    question: str

@app.post("/rag/ask")
def ask_question(request: QuestionRequest):
    """
    RAG 搜尋介面：
    1. 把使用者的問題轉成向量
    2. 去資料庫找最像的知識
    3. 回傳找到的知識 (目前先不做 LLM 生成，先做搜尋)
    """
    # 1. 將問題轉成向量
    query_vec = rag_model.encode(request.question, normalize_embeddings=True)
    
    # 2. 去資料庫搜尋 (這是 pgvector 最強的功能：<-> 代表歐幾里得距離)
    # 我們找最接近的 1 筆資料
    search_sql = text("""
        SELECT content, embedding <-> :query_vec AS distance
        FROM product_embeddings
        ORDER BY distance ASC
        LIMIT 1;
    """)
    
    # 執行 SQL
    with engine.connect() as conn:
        # 使用 .tolist() 確保轉成純 Python list，再轉字串
        result = conn.execute(search_sql, {"query_vec": str(query_vec.tolist())}).fetchone()
        
    if not result:
        return {"answer": "抱歉，我找不到相關資訊。"}
        
    # 3. 回傳結果
    best_match_content = result[0]
    distance = result[1]
    
    # 如果距離太遠 (代表問題跟知識庫無關)，可以設個門檻
    if distance > 1.5: # 門檻值可以測試調整
         return {"answer": "這個問題超出我的知識範圍。", "debug_content": best_match_content}

    return {
        "question": request.question,
        "retrieved_policy": best_match_content,
        "similarity_score": round(distance, 4)
    }