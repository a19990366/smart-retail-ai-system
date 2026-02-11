import pandas as pd
from sqlalchemy import create_engine
from prophet import Prophet
import joblib
import os

# 1. 資料庫連線
DEFAULT_DB_URL = 'postgresql://admin:000@localhost:5432/retail_ops'
DB_URL = os.getenv('DATABASE_URL', DEFAULT_DB_URL)

print(f"🔌 正在連線資料庫: {DB_URL}") # 印出來檢查用
engine = create_engine(DB_URL)

def get_all_products():
    """從資料庫找出所有獨一無二的商品 ID"""
    query = "SELECT DISTINCT product_id FROM sales_data"
    df = pd.read_sql(query, engine)
    return df['product_id'].tolist()

def train_model(product_id):
    print(f"🔄 正在處理商品: {product_id} ...")

    # 2. 撈取該商品的數據
    # 使用 f-string 小心 SQL Injection，但在內部系統且 product_id 可控的情況下暫時 OK
    query = f"SELECT transaction_date as ds, quantity as y FROM sales_data WHERE product_id = '{product_id}'"
    df = pd.read_sql(query, engine)
    
    # 格式轉換
    df['ds'] = pd.to_datetime(df['ds'])
    
    # 資料量檢查：如果資料太少 (例如少於 14 天)，Prophet 會報錯或不準
    if len(df) < 14:
        print(f"⚠️ 商品 {product_id} 資料不足 ({len(df)} 筆)，跳過訓練。")
        return

    # 3. 訓練
    model = Prophet(daily_seasonality=True)
    model.add_country_holidays(country_name='TW') # 加入台灣的假日資訊，讓模型更準確
    model.fit(df)

    # 4. 存檔
    os.makedirs('models', exist_ok=True)
    model_path = f'models/{product_id}.pkl'
    joblib.dump(model, model_path)
    
    print(f"✅ 商品 {product_id} 訓練完成！")

def main():
    print("🚀 啟動批次訓練系統...")
    products = get_all_products()
    print(f"📦 發現 {len(products)} 個商品，開始排程訓練...")
    
    for pid in products:
        try:
            train_model(pid)
        except Exception as e:
            print(f"❌ 商品 {pid} 訓練失敗: {e}")

    print("🎉 所有模型訓練作業結束。")

if __name__ == "__main__":
    main()