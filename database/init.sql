-- 1. 啟用 pgvector 擴充套件 (關鍵！)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 建立銷售數據表 (模擬訂單資料)
-- 這就是 Spring Boot 要寫入，Python 要讀取的表
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 建立索引以加快查詢速度 (針對日期，因為我們要撈 Time Series)
CREATE INDEX idx_sales_date ON sales_data(transaction_date);
CREATE INDEX idx_sales_product ON sales_data(product_id);

-- (預留) 之後給 RAG 用的向量表，先建起來也沒關係
CREATE TABLE IF NOT EXISTS product_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384) -- 對應 OpenAI 或常見模型的維度
);