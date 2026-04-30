# Data 目录 — 数据集说明与处理脚本

## 职责
本目录存放 Netflix Prize 原始数据集、清洗后的核心数据以及数据挖掘脚本。

## 文件清单

| 文件 | 格式 | 说明 |
|------|------|------|
| `archive/` | 目录 | Netflix Prize 原始数据集（4个评分文件 + 电影信息） |
| `ratings_clean.parquet` | Parquet | 清洗后的完整评分数据（~1亿条，推荐使用） |
| `ratings_clean.csv` | CSV | 采样版评分数据（200万条，便于直接查看） |
| `movies_clean.csv` | CSV | 清洗后的电影元数据（17,770部） |
| `data_mining.py` | 脚本 | 数据挖掘与特征工程全流程脚本（可重复执行） |
| `README.md` | 文档 | 本文件 — 数据目录说明 |

## 字段字典

### ratings_clean.parquet / ratings_clean.csv
- `MovieID` — 电影ID（1-17770）
- `CustomerID` — 匿名用户ID
- `Rating` — 评分（1-5 整型）
- `Date` — 评分日期（YYYY-MM-DD）

### movies_clean.csv
- `MovieID` — 电影ID
- `Year` — 上映年份（缺失值已用中位数填充）
- `Title` — 电影标题

## 对接说明
特征工程产出物在 `/features/` 目录，EDA 分析报告在 `/notebooks/` 目录。

## 数据生成
- 处理时间：2026-04-30
- 处理脚本：`data/data_mining.py`
- 原始来源：[Netflix Prize (Kaggle)](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data)
