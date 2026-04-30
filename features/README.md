# Features 目录 — 特征工程产出物

## 职责
本目录存放经过特征工程构建的用户特征矩阵、电影特征矩阵和时间特征数据。

## 文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| `user_features.csv` | 65 MB | 用户特征矩阵（480,189 用户 × 14 特征） |
| `movie_features.csv` | 1.8 MB | 电影特征矩阵（17,770 电影 × 13 特征） |
| `time_features_sample.csv` | 83 MB | 时间特征样例（200 万条 × 11 列） |

---

## 字段字典

### user_features.csv

| 字段 | 类型 | 说明 |
|------|------|------|
| `CustomerID` | int | 用户ID |
| `rating_count` | int | 用户评分总数 |
| `rating_mean` | float | 用户平均评分 |
| `rating_std` | float | 用户评分标准差 |
| `rating_min` | int | 用户最低评分（1-5） |
| `rating_max` | int | 用户最高评分（1-5） |
| `rating_median` | float | 用户评分中位数 |
| `rating_skew` | float | 用户评分偏度（分布对称性） |
| `first_date` | str | 首次评分日期 |
| `last_date` | str | 最近评分日期 |
| `active_days` | int | 活跃天数（首末评分间隔） |
| `rating_frequency` | float | 评分频率（条/月） |
| `high_rating_ratio` | float | 高分（≥4星）占比 |
| `activity_level` | str | 活跃度分档（very_low/low/medium/high/very_high） |

### movie_features.csv

| 字段 | 类型 | 说明 |
|------|------|------|
| `MovieID` | int | 电影ID |
| `rating_count` | int | 电影评分总数 |
| `rating_mean` | float | 电影平均评分 |
| `rating_std` | float | 电影评分标准差 |
| `rating_min` | int | 电影最低评分 |
| `rating_max` | int | 电影最高评分 |
| `rating_median` | float | 电影评分中位数 |
| `Year` | int | 上映年份 |
| `Title` | str | 电影标题 |
| `movie_age` | int | 电影年龄（截至2006年） |
| `title_length` | int | 标题字符数 |
| `era` | str | 年代标签（classic/vintage/eighties/nineties/modern） |
| `popularity_level` | str | 热度分档 |

### time_features_sample.csv

| 字段 | 类型 | 说明 |
|------|------|------|
| `CustomerID` | int | 用户ID |
| `MovieID` | int | 电影ID |
| `Rating` | int | 评分 |
| `rating_year` | int | 评分年份 |
| `rating_month` | int | 评分月份 |
| `rating_day` | int | 评分日 |
| `rating_dayofweek` | int | 星期几（0=周一, 6=周日） |
| `rating_weekend` | int | 是否周末（1=周末） |
| `rating_quarter` | int | 季度（1-4） |
| `rating_season` | str | 季节（spring/summer/fall/winter） |
| `days_since_2000` | int | 距离2000-01-01的天数 |

---

## 生成方式
- 基于 `data/ratings_clean.parquet` 清洗数据构建
- 全量聚合计算（用户和电影特征），时间特征采样200万条
- 处理脚本：`data/data_mining.py`
