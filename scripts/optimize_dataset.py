# -*- coding: utf-8 -*-
"""
数据集优化工具：对 Netflix 评分数据进行智能分层采样。
核心思想：用户评分越多 → 冗余越高 → 保留比例越低，
在保持评分分布和模型精度的前提下大幅减少训练数据量。

输出：data/ratings_optimized.parquet（可直接被训练脚本读取）
"""

import pandas as pd
import numpy as np
import os, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

print("=" * 60)
print("数据集优化工具：智能分层采样")
print("=" * 60)

# ============================================================
# 1. 加载全量数据
# ============================================================
print("\n[1/4] 加载全量评分数据...")
start = time.time()
df = pd.read_parquet(DATA_DIR / "ratings_clean.parquet", engine="pyarrow")
print(f"  OK 原始数据量：{len(df):,} 条")
print(f"  OK 用户数：{df['CustomerID'].nunique():,}")
print(f"  OK 电影数：{df['MovieID'].nunique():,}")
print(f"  OK 加载耗时：{time.time()-start:.1f}s")

# ============================================================
# 2. 分析用户活跃度分布
# ============================================================
print("\n[2/4] 分析用户活跃度分布...")
user_counts = df['CustomerID'].value_counts()
print(f"  用户评分量统计：")
print(f"    最小值：{user_counts.min()}")
print(f"    P25：  {user_counts.quantile(0.25):.0f}")
print(f"    中位数：{user_counts.median():.0f}")
print(f"    P75：  {user_counts.quantile(0.75):.0f}")
print(f"    最大值：{user_counts.max()}")
print(f"    均值：  {user_counts.mean():.1f}")

# 每档次用户数
for lo, hi, label in [(1, 5, '1-5'), (5, 20, '5-20'), (20, 50, '21-50'),
                       (50, 100, '51-100'), (100, 500, '101-500'), (500, 1e9, '500+')]:
    cnt = ((user_counts > lo) & (user_counts <= hi)).sum()
    print(f"    评分 {label:>7} 条：{cnt:>7,} 用户")

# ============================================================
# 3. 智能分层采样
# ============================================================
print("\n[3/4] 执行智能分层采样（用户越活跃，保留比例越低）...")

def get_sample_prob(count):
    """根据用户评分总数决定保留概率"""
    if count < 5:          # 极度低频 → 完全过滤（噪声 > 信号）
        return 0.00
    if count <= 20:        # 低频 → 全保留
        return 1.00
    if count <= 50:        # 中低频 → 保留 70%
        return 0.70
    if count <= 100:       # 中频 → 保留 50%
        return 0.50
    if count <= 500:       # 高频 → 保留 30%
        return 0.30
    return 0.20             # 超高頻(500+) → 保留 20%

# 向量化采样（避免逐行循环）
df['_user_count'] = df['CustomerID'].map(user_counts)
df['_sample_prob'] = df['_user_count'].apply(get_sample_prob)

np.random.seed(42)
df['_keep'] = np.random.random(len(df)) < df['_sample_prob']
df_opt = df[df['_keep']].copy()

# 额外过滤：低频电影（评分 < 10 条的电影信号太弱）
movie_counts = df_opt['MovieID'].value_counts()
active_movies = movie_counts[movie_counts >= 10].index
df_opt = df_opt[df_opt['MovieID'].isin(active_movies)]

# 清理辅助列
df_opt = df_opt.drop(columns=['_user_count', '_sample_prob', '_keep'])

print(f"  OK 优化后数据量：{len(df_opt):,} 条")
print(f"  OK 用户数：{df_opt['CustomerID'].nunique():,}")
print(f"  OK 电影数：{df_opt['MovieID'].nunique():,}")
print(f"  OK 压缩比：{len(df_opt) / len(df) * 100:.1f}%")

# ============================================================
# 4. 保存优化数据集
# ============================================================
print("\n[4/4] 保存优化后数据集...")
output_path = DATA_DIR / "ratings_optimized.parquet"
df_opt.to_parquet(output_path, index=False)
print(f"  OK 已保存至：{output_path}")
print(f"  OK 文件大小：{os.path.getsize(output_path) / 1e6:.1f} MB")
print(f"  OK 相对原始（664MB）：{os.path.getsize(output_path) / (664 * 1e6) * 100:.1f}%")

# ============================================================
# 5. 分布对比验证
# ============================================================
print("\n" + "=" * 60)
print("评分分布对比（优化前后应基本一致）")
print("=" * 60)
orig_dist = df['Rating'].value_counts(normalize=True).sort_index()
opt_dist = df_opt['Rating'].value_counts(normalize=True).sort_index()
print(f"{'评分':>6} | {'原始占比':>10} | {'优化后占比':>10} | {'偏差':>8}")
print("-" * 42)
for r in range(1, 6):
    o = orig_dist.get(r, 0) * 100
    p = opt_dist.get(r, 0) * 100
    print(f"{r:>6} | {o:>9.2f}% | {p:>9.2f}% | {p-o:>+7.2f}%")

user_orig = df['CustomerID'].nunique()
user_opt = df_opt['CustomerID'].nunique()
print(f"\n  用户数：{user_orig:,} → {user_opt:,}（保留 {user_opt/user_orig*100:.1f}%）")
print(f"  电影数：{df['MovieID'].nunique():,} → {df_opt['MovieID'].nunique():,}")
print(f"  原始用户均分：{df['Rating'].mean():.4f}")
print(f"  优化用户均分：{df_opt['Rating'].mean():.4f}")

print("\n" + "=" * 60)
print("== 优化完成！==")
print("=" * 60)
print("\n使用方式：将训练脚本的 data_path 改为 data/ratings_optimized.parquet 即可")
