# 模型评估报告

## 模型概览

| 模型 | 类型 | 说明 |
|------|------|------|
| ItemCF | 基于物品的协同过滤 | 计算电影间余弦相似度，基于用户历史评分加权预测 |
| ALS | 交替最小二乘矩阵分解 | PyTorch 实现，含用户/电影嵌入 + 偏置项 |

## 数据集

| 数据集 | 文件 | 规模 |
|--------|------|------|
| 小样本 | `data/ratings_clean.csv` | — |
| 全量 | `data/ratings_clean.parquet` | 约 1 亿条评分，480,189 用户，17,770 电影 |

## 超参数

详见 [configs/model_config.yaml](../configs/model_config.yaml)。

| 参数 | ItemCF | ALS |
|------|--------|-----|
| 嵌入维度 | — | 64 |
| 学习率 | — | 0.002 |
| 训练轮数 | — | 15 |
| 批次大小 | — | 16384 |
| 相似邻居数 | 10 | — |

## 离线指标

> 以下 RMSE 值为训练完成后实际输出，需补充。

| 模型 | 数据集 | RMSE |
|------|--------|------|
| ItemCF | 小样本 (CSV) | `待补充` |
| ALS | 小样本 (CSV) | `待补充` |
| ItemCF | 全量 (Parquet) | `待补充` |
| ALS | 全量 (Parquet) | `待补充` |

## RMSE 曲线

ALS 训练过程中记录的 RMSE 变化曲线保存为：
- `RMSE_models_small_csv.png`
- `RMSE_models_full_parquet.png`

## 训练环境

| 项目 | 版本 |
|------|------|
| Python | 3.x |
| PyTorch | `待补充` |
| Pandas | `待补充` |
| 计算设备 | CPU / GPU（`待补充`） |
| 训练耗时（小样本） | `待补充` |
| 训练耗时（全量） | `待补充` |

## 模型文件

| 文件 | 大小 | 包含内容 |
|------|------|----------|
| `models/item_cf_model_small.pkl` | — | 相似度矩阵 + 评分字典 |
| `models/als_model_small.pth` | — | ALS 模型参数 + ID 映射 |
| `models/movies_clean_small.csv` | — | 电影基本信息 |
