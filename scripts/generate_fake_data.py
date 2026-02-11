import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# 1. 設定資料庫連線 (連到剛剛 Docker 起來的 DB)
# 格式: postgresql://user:password@localhost:5432/dbname
db_url = 'postgresql://admin:000@localhost:5432/retail_ops'
engine = create_engine(db_url)

def generate_sales_data(product_id, days=90):
    """
    生成模擬銷售數據：帶有一些隨機波動和趨勢
    """
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    while current_date <= end_date:
        # 模擬：週末銷量較好，平日較差 (加入一些隨機性)
        base_sales = 50 if current_date.weekday() >= 5 else 20
        random_factor = np.random.randint(-5, 15)
        quantity = max(0, base_sales + random_factor) # 確保不為負數
        
        data.append({
            'product_id': product_id,
            'transaction_date': current_date.date(),
            'quantity': quantity
        })
        current_date += timedelta(days=1)
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("正在生成假資料...")
    
    # 模擬兩個商品的數據
    df_coffee = generate_sales_data("coffee_bean_001")
    df_tea = generate_sales_data("high_mountain_tea_002")
    
    combined_df = pd.concat([df_coffee, df_tea])
    
    print(f"生成完成，共 {len(combined_df)} 筆數據。")
    print(combined_df.head())

    # 2. 寫入資料庫
    try:
        combined_df.to_sql('sales_data', engine, if_exists='append', index=False)
        print("✅ 成功將數據寫入 PostgreSQL Docker 容器！")
    except Exception as e:
        print(f"❌ 寫入失敗: {e}")