import os
# 固定工作目录为项目根目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
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
    # ---------------------- 1. 执行 DDL ----------------------
    print("正在执行 schema.sql 建表...")
    schema_path = "db/schema.sql"
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        # 逐条执行 SQL 语句
        with engine.connect() as conn:
            for statement in schema_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
        print("✅ schema.sql 执行完成")
    else:
        print("⚠️ schema.sql 未找到，跳过建表")

    # ---------------------- 2. 导入数据 ----------------------
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

    # 写入数据库（追加模式，表已由 schema.sql 创建）
    print("正在写入 movies 表...")
    movies.to_sql("movies", engine, if_exists="append", index=False)
    print("movies 表写入完成")

    print("正在写入 ratings 表...")
    ratings.to_sql("ratings", engine, if_exists="append", index=False)
    print("ratings 表写入完成")

    print("正在写入 user_features 表...")
    user_features.to_sql("user_features", engine, if_exists="append", index=False)
    print("user_features 表写入完成")

    print("正在写入 movie_features 表...")
    movie_features.to_sql("movie_features", engine, if_exists="append", index=False)
    print("movie_features 表写入完成")

    # ---------------------- 3. 完成 ----------------------
    print("\n✅ 全部成功！数据库文件已生成：db/recommend.db")

except Exception as e:
    print(f"\n❌ 运行出错了！错误信息：{str(e)}")
    print("错误类型：", type(e).__name__)