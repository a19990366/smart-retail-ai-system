-- =====================================================
-- 1. 初始化環境與擴充套件
-- =====================================================
-- 啟用 pgvector 向量擴充套件 (RAG 核心)
CREATE EXTENSION IF NOT EXISTS vector;

-- 設定時區 (選用，建議設為台北時間)
SET timezone = 'Asia/Taipei';

-- =====================================================
-- 2. 舊有功能保留 (Prophet 預測用)
-- =====================================================
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_data(transaction_date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_data(product_id);

-- =====================================================
-- 3. RAG 知識庫系統架構 (核心功能)
-- =====================================================

-- [3.1] 分類管理表 (Categories)
-- 用於管理下拉選單的主分類 (e.g. 掃碼點餐, 支付設定)
CREATE TABLE IF NOT EXISTS categories (
    name TEXT PRIMARY KEY
);

-- [3.2] 標籤管理表 (Tags)
-- 用於管理多選標籤，並統計使用次數
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- [3.3] 知識庫主表 (Documents)
-- 存放文件內容、向量數據、統計數據
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,       -- 標題
    category TEXT REFERENCES categories(name) ON UPDATE CASCADE ON DELETE SET NULL, -- 關聯分類表
    outline TEXT,                      -- 大綱/摘要
    content TEXT NOT NULL,             -- 完整 Markdown 內容
    
    -- 核心向量欄位 (使用 paraphase-multilingual-MiniLM-L12-v2 模型，維度 384)
    embedding vector(384),             
    
    -- 統計數據
    helpful_count INT DEFAULT 0,       -- 有幫助次數
    unhelpful_count INT DEFAULT 0,     -- 沒幫助次數
    view_count INT DEFAULT 0,          -- 瀏覽次數
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- [3.4] 文章-標籤關聯表 (Document_Tags)
-- 實現多對多關係 (一篇文章多個標籤)
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, tag_id)
);

-- [3.5] 反饋紀錄表 (Feedback_Logs)
-- 詳細記錄使用者的反饋原因 (未來可以用來優化內容)
CREATE TABLE IF NOT EXISTS feedback_logs (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    action_type VARCHAR(20), -- 'helpful' or 'unhelpful'
    reason TEXT,             -- 使用者填寫的原因 (選填)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4. 索引優化 (效能關鍵)
-- =====================================================

-- [4.1] HNSW 向量索引 (大幅加速語義搜尋)
-- vector_cosine_ops 適用於餘弦相似度搜尋 (<=>)
-- 這裡假設資料量會變大，HNSW 是目前最快的向量索引演算法
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- [4.2] 一般欄位索引
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents USING gin(to_tsvector('english', title)); -- 簡單的關鍵字搜尋索引

-- =====================================================
-- 5. 預設資料初始化 (Seed Data)
-- =====================================================

-- [5.1] 初始化分類 (如果表是空的才插入)
INSERT INTO categories (name) VALUES 
    ('掃碼點餐'), 
    ('支付設定'), 
    ('會員系統'), 
    ('硬體設備'), 
    ('其他')
ON CONFLICT (name) DO NOTHING;

-- [5.2] 初始化常用標籤
INSERT INTO tags (name, usage_count) VALUES 
    ('Ocard', 0), 
    ('LinePay', 0), 
    ('UberEats', 0), 
    ('出單機', 0), 
    ('網路設定', 0)
ON CONFLICT (name) DO NOTHING;