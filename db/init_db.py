import pandas as pd
from sqlalchemy import create_engine, text
import os

print("脚本开始运行...")

# 确保 db 文件夹存在
if not os.path.exists("db"):
    os.makedirs("db")
    print("已创建 db 文件夹")

# 连接数据库
engine = create_engine("sqlite:///db/recommend.db")
print("数据库连接已创建")

try:
    # 读取数据
    print("正在读取 movies_clean.csv...")
    movies = pd.read_csv("data/movies_clean.csv")
    print("movies 读取成功，共", len(movies), "条数据")

    print("正在读取 ratings_clean.csv...")
    ratings = pd.read_csv("data/ratings_clean.csv")
    print("ratings 读取成功，共", len(ratings), "条数据")

    print("正在读取 user_features.csv...")
    user_features = pd.read_csv("features/user_features.csv")
    print("user_features 读取成功，共", len(user_features), "条数据")

    print("正在读取 movie_features.csv...")
    movie_features = pd.read_csv("features/movie_features.csv")
    print("movie_features 读取成功，共", len(movie_features), "条数据")

    # 写入数据库
    print("正在写入 movies 表...")
    movies.to_sql("movies", engine, if_exists="replace", index=False)
    print("movies 表写入完成")

    print("正在写入 ratings 表...")
    ratings.to_sql("ratings", engine, if_exists="replace", index=False)
    print("ratings 表写入完成")

    print("正在写入 user_features 表...")
    user_features.to_sql("user_features", engine, if_exists="replace", index=False)
    print("user_features 表写入完成")

    print("正在写入 movie_features 表...")
    movie_features.to_sql("movie_features", engine, if_exists="replace", index=False)
    print("movie_features 表写入完成")

    print("\n✅ 全部成功！数据库文件已生成：db/recommend.db")

    # ---------------------- 新增：创建推荐结果缓存表 ----------------------
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS rec_cache (
            user_id INTEGER PRIMARY KEY,
            rec_movies TEXT NOT NULL,
            expire_time TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        conn.commit()
    print("✅ 推荐结果缓存表创建完成！")

except Exception as e:
    print(f"\n❌ 运行出错了！错误信息：{str(e)}")
    print("错误类型：", type(e).__name__)