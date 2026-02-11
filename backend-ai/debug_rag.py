# backend-ai/debug_rag.py
from sentence_transformers import SentenceTransformer
import numpy as np

def test_model():
    model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
    print(f"🛠 正在載入模型: {model_name}")
    model = SentenceTransformer(model_name)
    
    # 模擬你的情況
    doc_text = "運費說明：全館消費滿 1000 元免運費，未滿則收 80 元運費。"
    query_text = "運費"
    
    # 轉向量
    doc_vec = model.encode(doc_text, normalize_embeddings=True)
    query_vec = model.encode(query_text, normalize_embeddings=True)
    
    # 手動算歐幾里得距離 (Euclidean Distance)
    # 這就是 pgvector <-> 做的事情
    distance = np.linalg.norm(doc_vec - query_vec)
    
    print(f"------------ 測試結果 ------------")
    print(f"文件: {doc_text}")
    print(f"問題: {query_text}")
    print(f"計算出的距離 (Distance): {distance}")
    print(f"--------------------------------")

    if distance > 1.5:
        print("❌ 距離太大！這代表模型認為兩者不相關 (或模型壞了)。")
    else:
        print("✅ 距離正常！這代表模型沒問題，是資料庫的問題。")

if __name__ == "__main__":
    test_model()