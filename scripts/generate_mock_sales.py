import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import holidays

def generate_sales_csv():
    # 1. 設定：產生過去 1 年的數據
    end_date = datetime.now()
    start_date = end_date - timedelta(days=500)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 2. 取得台灣節假日清單 (繁體中文環境建議用 TW)
    tw_holidays = holidays.TW(years=[start_date.year, end_date.year])
    
    data = []
    base_sales = 100
    growth_rate = 0.1 # 每日微幅成長趨勢
    
    for i, date in enumerate(dates):
        # A. 基礎銷量 + 整體趨勢
        current_base = base_sales + (i * growth_rate)
        
        # B. 判斷是否為節假日 (加成 50%)
        # holidays 函式庫支援直接用 date 物件判斷
        is_holiday = date in tw_holidays
        multiplier = 1.0
        
        if is_holiday:
            multiplier = 1.5 # 節假日賣更好 (50% 成長)
            print(f"🎉 節假日加成: {date.strftime('%Y-%m-%d')} ({tw_holidays.get(date)})")
        elif date.weekday() >= 4:
            multiplier = 1.2 # 一般週末加成 (20%)
            
        # C. 計算最終銷量 + 隨機雜訊
        daily_sales = current_base * multiplier
        noise = random.randint(-15, 30)
        final_qty = int(daily_sales + noise)
        
        if final_qty < 0: final_qty = 0
            
        data.append({
            "product_id": "item_001",
            "transaction_date": date.strftime("%Y-%m-%d"),
            "quantity": final_qty
        })
        
    df = pd.DataFrame(data)
    filename = "sales_mock.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ 已生成含有節假日特徵的假資料: {filename} ({len(df)} 筆)")

if __name__ == "__main__":
    generate_sales_csv()