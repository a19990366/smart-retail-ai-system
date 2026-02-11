import os
import pandas as pd
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer

# 1. 資料庫連線
DEFAULT_DB_URL = 'postgresql://admin:000@localhost:5432/retail_ops'
DB_URL = os.getenv('DATABASE_URL', DEFAULT_DB_URL)
engine = create_engine(DB_URL)

# 2. 準備假知識
knowledge_base = [
    "退貨政策：商品購買後 7 天內，憑發票可無條件退換貨。",
    "會員權益：累積消費滿 5000 元可升級為 VIP，享有 9 折優惠。",
    "營業時間：平日 09:00 - 22:00，週末及國定假日 10:00 - 23:00。",
    "特殊節日：農曆新年期間 (除夕至初三) 暫停營業。",
    "咖啡豆保存：建議將咖啡豆存放於不透光密封罐，並置於陰涼處，不可冷凍。",
    "運費說明：全館消費滿 1000 元免運費，未滿則收 80 元運費。"
]

def ingest_data():
    print("📚 正在下載 Embedding 模型 (若已下載則會略過)...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    print("🔄 正在將文字轉換為向量...")
    embeddings = model.encode(knowledge_base, normalize_embeddings=True)
    
    # [關鍵修正] 將 Numpy Array 轉為 Python List，否則 psycopg2 會報錯
    embeddings_list = [emb.tolist() for emb in embeddings]
    
    print("💾 正在寫入 PostgreSQL (pgvector)...")
    
    df = pd.DataFrame({
        'content': knowledge_base,
        'embedding': embeddings_list
    })

    # 使用 transaction 清空舊資料
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE product_embeddings RESTART IDENTITY;"))
        conn.commit()
        
    # 寫入資料庫
    df.to_sql('product_embeddings', engine, if_exists='append', index=False)
    
    print(f"✅ 成功寫入 {len(df)} 筆知識！你的資料庫現在懂這些規則了。")

if __name__ == "__main__":
    ingest_data()