-- ========================================
-- 电影推荐系统 — 数据库 Schema
-- 数据库类型：SQLite
-- ========================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    -- 用户特征由 feature 表管理，此处仅保留核心标识
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 电影表
CREATE TABLE IF NOT EXISTS movies (
    movie_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    genres TEXT,
    year INTEGER
);

-- 评分记录表
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK(rating >= 0.5 AND rating <= 5.0),
    timestamp INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_movie ON ratings(movie_id);

-- 用户特征表
CREATE TABLE IF NOT EXISTS user_features (
    user_id INTEGER PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    occupation TEXT,
    -- 其他特征字段由 EDA 确定后补充
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 电影特征表
CREATE TABLE IF NOT EXISTS movie_features (
    movie_id INTEGER PRIMARY KEY,
    -- 特征向量或标签序列化字段（JSON / 逗号分隔），具体格式由 A、B 商定
    feature_vector TEXT,
    tag TEXT,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- 推荐结果缓存表
CREATE TABLE IF NOT EXISTS rec_cache (
    user_id INTEGER PRIMARY KEY,
    rec_movies TEXT NOT NULL,
    expire_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
