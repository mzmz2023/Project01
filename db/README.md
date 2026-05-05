# db — 数据库

## 职责

数据库 Schema 定义、初始化脚本、数据文件。

## 文件说明

| 文件 | 说明 |
|------|------|
| `schema.sql` | 数据库 DDL，定义全部 6 张表的结构（主键、外键、索引、约束） |
| `init_db.py` | 数据库初始化脚本：执行 schema.sql 建表 → 从 CSV 导入数据 |
| `recommend.db` | SQLite 数据库文件（已生成） |

## 表结构

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `users` | 用户表 | user_id |
| `movies` | 电影表 | movie_id, title, genres, year |
| `ratings` | 评分记录表 | user_id, movie_id, rating, timestamp |
| `user_features` | 用户特征表 | user_id, age, gender, occupation |
| `movie_features` | 电影特征表 | movie_id, feature_vector, tag |
| `rec_cache` | 推荐结果缓存 | user_id, rec_movies, expire_time |

## 初始化

```bash
python db/init_db.py
```

数据来源：

- `data/movies_clean.csv` — A 同学清洗后的电影数据
- `data/ratings_clean.csv` — A 同学清洗后的评分数据
- `features/user_features.csv` — A 同学产出的用户特征
- `features/movie_features.csv` — A 同学产出的电影特征
