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

-- 用户特征表（列定义与 features/user_features.csv 一致）
CREATE TABLE IF NOT EXISTS user_features (
    CustomerID INTEGER PRIMARY KEY,
    rating_count INTEGER,
    rating_mean REAL,
    rating_std REAL,
    rating_min INTEGER,
    rating_max INTEGER,
    rating_median REAL,
    rating_skew REAL,
    first_date TEXT,
    last_date TEXT,
    active_days INTEGER,
    rating_frequency REAL,
    high_rating_ratio REAL,
    activity_level TEXT
);

-- 电影特征表（列定义与 features/movie_features.csv 一致）
CREATE TABLE IF NOT EXISTS movie_features (
    MovieID INTEGER PRIMARY KEY,
    rating_count INTEGER,
    rating_mean REAL,
    rating_std REAL,
    rating_min INTEGER,
    rating_max INTEGER,
    rating_median REAL,
    Year INTEGER,
    Title TEXT,
    movie_age INTEGER,
    title_length INTEGER,
    era TEXT,
    popularity_level TEXT
);

-- 推荐结果缓存表
CREATE TABLE IF NOT EXISTS rec_cache (
    user_id INTEGER PRIMARY KEY,
    rec_movies TEXT NOT NULL,
    expire_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
