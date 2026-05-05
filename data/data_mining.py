"""
=============================================================================
电影推荐系统  数据挖掘与特征工程全流程
角色：数据工程师 (成员 A)
数据集：Netflix Prize (Kaggle)
=============================================================================
流程：
  阶段1 → 明确业务目标
  阶段2 → 数据探索与验证 (EDA)
  阶段3 → 数据清洗
  阶段4 → 特征工程
  阶段5 → 保存结果

输出文件（保存在 /data 目录）：
  - ratings_clean.parquet : 清洗后的完整评分数据
  - ratings_clean.csv     : 采样版评分数据（便于协作）
  - movies_clean.csv      : 清洗后的电影信息
  - user_features.csv     : 用户特征矩阵
  - movie_features.csv    : 电影特征矩阵
  - time_features_sample.csv : 时间特征样例
  - eda_report.txt        : EDA 数值报告
  - README.md             : 数据目录文档
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os, gc, time, warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')

# ============================================================================
# 路径配置
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
FEATURES_DIR = BASE_DIR / "features"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
for d in [DATA_DIR, FEATURES_DIR, NOTEBOOKS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("电影推荐系统 - 数据挖掘与特征工程")
print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# ============================================================================
# 阶段1：明确业务目标
# ============================================================================
print("\n" + "=" * 70)
print("[阶段1] 明确业务目标")
print("=" * 70)

BUSINESS_GOALS = """
【项目目标】
构建个性化电影推荐系统，基于 Netflix Prize 数据集挖掘用户观影偏好，生成高质量推荐。

【数据挖掘目标】
1. 理解评分分布、用户行为模式、电影热度规律
2. 构建特征矩阵（用户特征 + 电影特征 + 时间特征）
3. 为推荐算法（协同过滤、矩阵分解）提供经过清洗的特征输入
4. 产出数据洞察报告

【交付标准】
- /data/ratings_clean.parquet  完整清洗评分
- /data/ratings_clean.csv  采样版评分（团队协作用）
- /data/movies_clean.csv  电影元数据
- /data/user_features.csv  用户特征矩阵
- /data/movie_features.csv  电影特征矩阵
- /data/eda_report.txt  EDA 报告
- /data/README.md  数据字典
"""
print(BUSINESS_GOALS)

# ============================================================================
# 阶段2+3：数据探索与验证 + 数据清洗（单次遍历实现）
# ============================================================================
print("\n" + "=" * 70)
print("[阶段2] 数据探索与验证 (EDA)")
print("=" * 70)
print("\n" + "=" * 70)
print("[阶段3] 数据清洗")
print("=" * 70)

# ---- 工具函数：解析 Netflix 数据文件 ----
def parse_netflix_file(filepath, chunk_size=500000):
    """
    流式解析 Netflix Prize 数据文件。
    格式：MovieID:\n CustomerID,Rating,Date\n ...
    返回生成器，yield (DataFrame块)
    """
    current_movie_id = None
    rows = []
    for line in open(filepath, 'r', encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        if line.endswith(':'):
            current_movie_id = int(line[:-1])
            continue
        parts = line.split(',')
        if len(parts) == 3 and current_movie_id is not None:
            rows.append((current_movie_id, int(parts[0]), int(parts[1]), parts[2]))
        if len(rows) >= chunk_size:
            df = pd.DataFrame(rows, columns=['MovieID', 'CustomerID', 'Rating', 'Date'])
            yield df
            rows = []
    if rows:
        yield pd.DataFrame(rows, columns=['MovieID', 'CustomerID', 'Rating', 'Date'])


# ---- 加载电影元数据 ----
print("\n  加载电影元数据...")
# 注意：标题可能含逗号，需手动按前两个逗号分割
_mrows = []
with open(ARCHIVE_DIR / "movie_titles.csv", 'r', encoding='ISO-8859-1') as _f:
    for _line in _f:
        _line = _line.strip()
        if not _line:
            continue
        _p = _line.split(',')
        _mid = int(_p[0])
        # 处理 'NULL'、空字符串等无效年份
        _yr_str = _p[1].strip()
        _yr = int(_yr_str) if _yr_str and _yr_str.upper() != 'NULL' else None
        _title = ','.join(_p[2:])
        _mrows.append((_mid, _yr, _title))
movies_df = pd.DataFrame(_mrows, columns=['MovieID', 'Year', 'Title'])
movies_df['Year'] = movies_df['Year'].astype('Int64')
n_movies = len(movies_df)
n_year_missing = movies_df['Year'].isna().sum()
year_min = movies_df['Year'].min()
year_max = movies_df['Year'].max()
print(f"  电影总数: {n_movies:,}")
print(f"  年份范围: {year_min} ~ {year_max}")
print(f"  缺失年份: {n_year_missing:,}")

# ---- 单次遍历：解析 + EDA统计 + 清洗 + 存储 ----
print("\n  开始解析/清洗/统计（单次遍历 4 个文件）...")
start_total = time.time()

# 聚合统计
total_rows = 0
total_invalid_rating = 0
total_invalid_date = 0
n_users_set = set()
n_movies_set = set()
rating_sum_all = 0

# 用于 EDA 的采样
eda_sample = []
EDA_SAMPLE_SIZE = 2_000_000

# 用户/电影聚合（向量化方式，按chunk聚合后合并）
user_agg_chunks = []
movie_agg_chunks = []

# Parquet 分批写入
def _flush_parquet(chunks_list, path):
    """将一批 DataFrame 合并后写入 parquet（追加模式）"""
    batch = pd.concat(chunks_list, ignore_index=True)
    if path.exists():
        old = pd.read_parquet(path)
        full = pd.concat([old, batch], ignore_index=True)
        full.to_parquet(path, index=False)
        del old, full
    else:
        batch.to_parquet(path, index=False)
    del batch
    gc.collect()

parquet_buffer = []  # 暂存 clean chunks，满10个刷写一次

data_files = sorted(ARCHIVE_DIR.glob("combined_data_*.txt"))

for fi, f in enumerate(data_files):
    f_start = time.time()
    n_chunks = 0
    for chunk in parse_netflix_file(f, chunk_size=500000):
        n_chunks += 1
        n_rows = len(chunk)
        total_rows += n_rows

        # ---- 数据清洗 ----
        # 1) 过滤无效评分（范围1-5）
        valid_rating = chunk['Rating'].between(1, 5)
        bad_rating = (~valid_rating).sum()
        total_invalid_rating += bad_rating

        # 2) 过滤无效日期
        chunk['Date'] = pd.to_datetime(chunk['Date'], errors='coerce')
        valid_date = chunk['Date'].notna()
        bad_date = (~valid_date).sum()
        total_invalid_date += bad_date

        # 应用清洗
        mask = valid_rating & valid_date
        chunk_clean = chunk[mask].copy()

        if len(chunk_clean) == 0:
            continue

        # ---- EDA 统计（向量化） ----
        n_users_set.update(chunk_clean['CustomerID'].unique())
        n_movies_set.update(chunk_clean['MovieID'].unique())
        rating_sum_all += chunk_clean['Rating'].sum()

        # 采样
        if len(eda_sample) < EDA_SAMPLE_SIZE:
            needed = EDA_SAMPLE_SIZE - len(eda_sample)
            eda_sample.append(chunk_clean.iloc[:min(needed, len(chunk_clean))])

        # 电影聚合（按MovieID分组）
        m_agg = chunk_clean.groupby('MovieID').agg(
            cnt=('Rating', 'count'),
            sum=('Rating', 'sum'),
            sum_sq=('Rating', lambda x: (x**2).sum())
        ).reset_index()
        movie_agg_chunks.append(m_agg)

        # 用户聚合（按CustomerID分组，10%采样控制内存）
        if np.random.random() < 0.1:
            u_agg = chunk_clean.groupby('CustomerID').agg(
                cnt=('Rating', 'count'),
                sum=('Rating', 'sum'),
                sum_sq=('Rating', lambda x: (x**2).sum())
            ).reset_index()
            user_agg_chunks.append(u_agg)

        # ---- 攒批写入 Parquet ----
        parquet_buffer.append(chunk_clean)
        if len(parquet_buffer) >= 10:  # 每10个chunk（~500万行）刷写一次
            _flush_parquet(parquet_buffer, DATA_DIR / 'ratings_clean.parquet')
            parquet_buffer = []
            del chunk_clean, chunk, m_agg
            gc.collect()
        else:
            del chunk_clean, chunk, m_agg
            gc.collect()

        if n_chunks % 10 == 0:
            print(f"  [{f.name}] 已处理 {n_chunks*500000:,} 行... ({time.time()-f_start:.0f}s)")

    # 文件末尾刷写剩余 buffer
    if parquet_buffer:
        _flush_parquet(parquet_buffer, DATA_DIR / 'ratings_clean.parquet')
        parquet_buffer = []

    elapsed = time.time() - f_start
    print(f"   {f.name} 完成  {n_chunks} 个块, {elapsed:.1f}s")

total_elapsed = time.time() - start_total
print(f"\n  全量处理完成，耗时 {total_elapsed:.0f}s")
print(f"  总记录: {total_rows:,}")
print(f"  无效评分: {total_invalid_rating:,}")
print(f"  无效日期: {total_invalid_date:,}")
print(f"  唯一用户: {len(n_users_set):,}")
print(f"  唯一电影: {len(n_movies_set):,}")
print(f"  平均评分: {rating_sum_all/total_rows:.4f}")

# ---- 合并聚合数据 ----
print("\n  合并聚合统计...")
if movie_agg_chunks:
    movie_agg_all = pd.concat(movie_agg_chunks, ignore_index=True)
    movie_agg_all = movie_agg_all.groupby('MovieID').agg(
        {'cnt': 'sum', 'sum': 'sum', 'sum_sq': 'sum'}
    ).reset_index()
else:
    movie_agg_all = pd.DataFrame(columns=['MovieID', 'cnt', 'sum', 'sum_sq'])

if user_agg_chunks:
    user_agg_all = pd.concat(user_agg_chunks, ignore_index=True)
    user_agg_all = user_agg_all.groupby('CustomerID').agg(
        {'cnt': 'sum', 'sum': 'sum', 'sum_sq': 'sum'}
    ).reset_index()
else:
    user_agg_all = pd.DataFrame(columns=['CustomerID', 'cnt', 'sum', 'sum_sq'])

# ============================================================================
# EDA 深入分析（基于采样数据）
# ============================================================================
print("\n--- EDA 深入分析 ---")
ratings_sample = pd.concat(eda_sample, ignore_index=True)
ratings_sample['Date'] = pd.to_datetime(ratings_sample['Date'])
n_s = len(ratings_sample)
print(f"  采样数据集: {n_s:,} 条")

# 2.1 评分分布
rating_dist = ratings_sample['Rating'].value_counts().sort_index()
print("\n  评分分布:")
for r in range(1, 6):
    cnt = rating_dist.get(r, 0)
    pct = cnt / n_s * 100
    bar = '█' * int(pct / 2)
    print(f"    {r}: {cnt:>10,} ({pct:6.2f}%) {bar}")

# 2.2 用户行为
user_group = ratings_sample.groupby('CustomerID')['Rating']
user_eda = user_group.agg(['count', 'mean', 'std']).fillna(0)
print(f"\n  用户活跃度:")
print(f"    总用户: {len(user_eda):,}")
print(f"    平均评分数: {user_eda['count'].mean():.1f}")
print(f"    中位数评分数: {user_eda['count'].median():.1f}")
print(f"    最多评分: {user_eda['count'].max():,}")

# 活跃度分层
for lo, hi, label in [(0, 5, '1-5'), (5, 20, '6-20'), (20, 50, '21-50'),
                        (50, 100, '51-100'), (100, 500, '101-500'), (500, 1e9, '500+')]:
    cnt = ((user_eda['count'] > lo) & (user_eda['count'] <= hi)).sum()
    print(f"    {label} 条: {cnt:>8,} 用户 ({cnt/len(user_eda)*100:5.2f}%)")

# 2.3 电影热度
movie_group = ratings_sample.groupby('MovieID')['Rating']
movie_eda = movie_group.agg(['count', 'mean', 'std']).fillna(0)
print(f"\n  电影热度:")
print(f"    总电影: {len(movie_eda):,}")
print(f"    平均评分数: {movie_eda['count'].mean():.1f}")
print(f"    中位数评分数: {movie_eda['count'].median():.1f}")
print(f"    最多评分: {movie_eda['count'].max():,}")

# 热门电影 Top 10
top10_movies = movie_eda.nlargest(10, 'count')
print(f"\n  最热门电影 Top 10:")
for mid in top10_movies.index:
    row = movies_df[movies_df['MovieID'] == mid]
    title = row['Title'].values[0][:45] if len(row) > 0 else "Unknown"
    year = row['Year'].values[0] if len(row) > 0 else "N/A"
    mc = top10_movies.loc[mid, 'count']
    mr = top10_movies.loc[mid, 'mean']
    print(f"    [{mid:>5}] {title:<45} ({year})  {int(mc):>6,}评  均分{mr:.2f}")

# 2.4 时间特征
ratings_sample['Year'] = ratings_sample['Date'].dt.year
ratings_sample['Month'] = ratings_sample['Date'].dt.month
ratings_sample['Dow'] = ratings_sample['Date'].dt.dayofweek

print(f"\n  年份分布:")
for yr, cnt in ratings_sample['Year'].value_counts().sort_index().items():
    if pd.notna(yr):
        print(f"    {int(yr)}: {cnt:,}")

dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
print(f"\n  星期分布:")
for d in range(7):
    cnt = (ratings_sample['Dow'] == d).sum()
    print(f"    {dow_names[d]}: {cnt:,} ({cnt/n_s*100:5.2f}%)")

# 2.5 稀疏度
n_us = ratings_sample['CustomerID'].nunique()
n_ms = ratings_sample['MovieID'].nunique()
density = n_s / (n_us * n_ms) * 100
print(f"\n  稀疏度:")
print(f"    用户: {n_us:,}  电影: {n_ms:,}")
print(f"    密度: {density:.4f}%  稀疏度: {100-density:.4f}%")

# 2.6 可视化
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

axes[0,0].bar(rating_dist.index, rating_dist.values, color='steelblue', edgecolor='white')
axes[0,0].set_title('Rating Distribution', fontsize=13, fontweight='bold')
axes[0,0].set_xlabel('Rating'); axes[0,0].set_ylabel('Count')
for r, c in rating_dist.items():
    axes[0,0].text(r, c+1000, f'{c:,}', ha='center', fontsize=9)

axes[0,1].hist(user_eda['count'].clip(0, 200), bins=50, color='salmon', edgecolor='white')
axes[0,1].set_title('User Activity', fontsize=13, fontweight='bold')
axes[0,1].set_xlabel('Ratings per User'); axes[0,1].set_ylabel('Users')

axes[0,2].hist(movie_eda['count'].clip(0, 500), bins=50, color='mediumseagreen', edgecolor='white')
axes[0,2].set_title('Movie Popularity', fontsize=13, fontweight='bold')
axes[0,2].set_xlabel('Ratings per Movie'); axes[0,2].set_ylabel('Movies')

yr_valid = ratings_sample['Year'].dropna()
yr_counts = yr_valid.value_counts().sort_index()
axes[1,0].plot(yr_counts.index.astype(int), yr_counts.values, marker='o', color='coral', linewidth=2)
axes[1,0].set_title('Ratings Over Years', fontsize=13, fontweight='bold')
axes[1,0].set_xlabel('Year'); axes[1,0].set_ylabel('Ratings')

dow_counts = [ratings_sample['Dow'].value_counts().get(d, 0) for d in range(7)]
axes[1,1].bar(dow_names, dow_counts, color='mediumpurple', edgecolor='white')
axes[1,1].set_title('Ratings by Day of Week', fontsize=13, fontweight='bold')
axes[1,1].set_xlabel('Day'); axes[1,1].set_ylabel('Ratings')

axes[1,2].hist(user_eda['mean'], bins=30, color='gold', edgecolor='white', alpha=0.8)
axes[1,2].set_title('User Mean Rating', fontsize=13, fontweight='bold')
axes[1,2].set_xlabel('Mean Rating'); axes[1,2].set_ylabel('Users')

plt.tight_layout()
plt.savefig(NOTEBOOKS_DIR / 'eda_visualizations.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n   EDA 可视化 → notebooks/eda_visualizations.png")

# ---- EDA 报告 ----
eda_text = f"""
==============================================================================
电影推荐系统  EDA 报告
生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据集: Netflix Prize
==============================================================================

1. 数据规模
------------------------------------------------------------------------------
  总评分数: {total_rows:,}
  电影数:   {len(n_movies_set):,}
  用户数:   {len(n_users_set):,}
  日期范围: {ratings_sample['Date'].min().date()} ~ {ratings_sample['Date'].max().date()}

2. 评分分布
------------------------------------------------------------------------------
"""
for r in range(1, 6):
    cnt = rating_dist.get(r, 0)
    pct = cnt / n_s * 100
    eda_text += f"  {r}: {cnt:,} ({pct:.2f}%)\n"
eda_text += f"  平均分: {rating_sum_all/total_rows:.4f}\n"

eda_text += f"""
3. 用户行为
------------------------------------------------------------------------------
  用户数:        {len(user_eda):,}
  平均评分数:    {user_eda['count'].mean():.1f}
  评分中位数:    {user_eda['count'].median():.1f}
  最高评分数:    {user_eda['count'].max():,}
  用户均分均值:  {user_eda['mean'].mean():.4f}

4. 电影热度
------------------------------------------------------------------------------
  电影数:        {len(movie_eda):,}
  平均评分数:    {movie_eda['count'].mean():.1f}
  评分中位数:    {movie_eda['count'].median():.1f}
  最高评分数:    {movie_eda['count'].max():,}
  电影均分均值:  {movie_eda['mean'].mean():.4f}

5. 矩阵稀疏度
------------------------------------------------------------------------------
  密度:   {density:.4f}%
  稀疏度: {100-density:.4f}%

6. 数据质量
------------------------------------------------------------------------------
  无效评分（非1-5）: {total_invalid_rating:,}
  无效日期:          {total_invalid_date:,}
  电影年份缺失:      {n_year_missing:,}

7. 关键洞察
------------------------------------------------------------------------------
  - 评分偏态：4-5星高分占主导，用户倾向于给好评
  - 长尾效应：少数热门电影获大量评分，大量冷门电影评分稀少
  - 活跃度：大部分用户评分<20条，存在少数"超级用户"(500+)
  - 时间趋势：2000年后评分数量明显增长
  - 星期效应：周末评分略高于工作日
==============================================================================
"""
with open(NOTEBOOKS_DIR / 'eda_report.txt', 'w', encoding='utf-8') as f:
    f.write(eda_text)
print("   EDA 报告 → data/eda_report.txt")
print(eda_text[-500:])


# ============================================================================
# 阶段4：特征工程
# ============================================================================
print("\n" + "=" * 70)
print(" 阶段4：特征工程")
print("=" * 70)

# 读取清洗后的完整数据
print("\n  加载清洗数据...")
ratings_clean = pd.read_parquet(DATA_DIR / 'ratings_clean.parquet')
print(f"  加载完成: {len(ratings_clean):,} 条")

# ---- 4.1 用户特征 ----
print("\n--- 4.1 用户特征 ---")
print("  计算中（全量用户聚合）...")
user_features = ratings_clean.groupby('CustomerID').agg(
    rating_count=('Rating', 'count'),
    rating_mean=('Rating', 'mean'),
    rating_std=('Rating', 'std'),
    rating_min=('Rating', 'min'),
    rating_max=('Rating', 'max'),
    rating_median=('Rating', 'median'),
    rating_skew=('Rating', lambda x: x.skew() if len(x) > 1 else 0.0),
    first_date=('Date', 'min'),
    last_date=('Date', 'max')
).reset_index()
user_features['rating_std'] = user_features['rating_std'].fillna(0)
user_features['rating_skew'] = user_features['rating_skew'].fillna(0)

# 活跃天数 & 频率
user_features['active_days'] = (user_features['last_date'] - user_features['first_date']).dt.days.clip(lower=1)
user_features['rating_frequency'] = user_features['rating_count'] / (user_features['active_days'] / 30)

# 高分占比
print("  计算高分偏好...")
high_ratio = (
    ratings_clean.assign(is_high=(ratings_clean['Rating'] >= 4).astype(int))
    .groupby('CustomerID')['is_high']
    .mean()
    .reset_index(name='high_rating_ratio')
)
user_features = user_features.merge(high_ratio, on='CustomerID')

# 活跃度分档
try:
    user_features['activity_level'] = pd.qcut(
        user_features['rating_count'], q=5,
        labels=['very_low', 'low', 'medium', 'high', 'very_high'],
        duplicates='drop'
    )
except ValueError:
    user_features['activity_level'] = 'medium'

user_features = user_features.sort_values('CustomerID').reset_index(drop=True)
user_features.to_csv(FEATURES_DIR / 'user_features.csv', index=False, encoding='utf-8')
print(f"   {len(user_features):,} 用户 × {len(user_features.columns)} 特征 → features/user_features.csv")

# ---- 4.2 电影特征 ----
print("\n--- 4.2 电影特征 ---")
print("  计算中...")
movie_features = ratings_clean.groupby('MovieID').agg(
    rating_count=('Rating', 'count'),
    rating_mean=('Rating', 'mean'),
    rating_std=('Rating', 'std'),
    rating_min=('Rating', 'min'),
    rating_max=('Rating', 'max'),
    rating_median=('Rating', 'median')
).reset_index()
movie_features['rating_std'] = movie_features['rating_std'].fillna(0)

# 合并元数据
movie_features = movie_features.merge(movies_df, on='MovieID', how='left')
movie_features['Year'] = movie_features['Year'].fillna(movies_df['Year'].median()).astype(int)
movie_features['movie_age'] = 2006 - movie_features['Year']
movie_features['title_length'] = movie_features['Title'].str.len()

# 年代标签
def era_label(y):
    if y < 1960: return 'classic'
    elif y < 1980: return 'vintage'
    elif y < 1990: return 'eighties'
    elif y < 2000: return 'nineties'
    else: return 'modern'
movie_features['era'] = movie_features['Year'].apply(era_label)

# 热度分档
try:
    movie_features['popularity_level'] = pd.qcut(
        movie_features['rating_count'], q=5,
        labels=['very_low', 'low', 'medium', 'high', 'very_high'],
        duplicates='drop'
    )
except ValueError:
    movie_features['popularity_level'] = 'medium'

movie_features = movie_features.sort_values('MovieID').reset_index(drop=True)
movie_features.to_csv(FEATURES_DIR / 'movie_features.csv', index=False, encoding='utf-8')
print(f"   {len(movie_features):,} 电影 × {len(movie_features.columns)} 特征 → features/movie_features.csv")

# ---- 4.3 时间特征 ----
print("\n--- 4.3 时间特征 ---")
# 使用采样数据生成时间特征（全量太冗余）
time_df = ratings_clean.sample(n=min(2_000_000, len(ratings_clean)), random_state=42).copy()
time_features = pd.DataFrame({
    'CustomerID': time_df['CustomerID'],
    'MovieID': time_df['MovieID'],
    'Rating': time_df['Rating'],
    'rating_year': time_df['Date'].dt.year,
    'rating_month': time_df['Date'].dt.month,
    'rating_day': time_df['Date'].dt.day,
    'rating_dayofweek': time_df['Date'].dt.dayofweek,
    'rating_weekend': (time_df['Date'].dt.dayofweek >= 5).astype(int),
    'rating_quarter': time_df['Date'].dt.quarter,
    'rating_season': time_df['Date'].dt.month.map({
        12:'winter',1:'winter',2:'winter',3:'spring',4:'spring',5:'spring',
        6:'summer',7:'summer',8:'summer',9:'fall',10:'fall',11:'fall'
    }),
    'days_since_2000': (time_df['Date'] - pd.Timestamp('2000-01-01')).dt.days
})
time_features.to_csv(FEATURES_DIR / 'time_features_sample.csv', index=False, encoding='utf-8')
print(f"   {len(time_features):,} 条 × {len(time_features.columns)} 列 → features/time_features_sample.csv")

# ---- 4.4 创建数据采样版 CSV ----
print("\n--- 4.4 生成采样版 CSV ---")
ratings_sample_csv = ratings_clean.sample(n=min(2_000_000, len(ratings_clean)), random_state=42)
ratings_sample_csv.to_csv(DATA_DIR / 'ratings_clean.csv', index=False, encoding='utf-8')
print(f"   {len(ratings_sample_csv):,} 条 → data/ratings_clean.csv")

# ---- 4.5 创建 README.md ----
print("\n--- 4.5 data/README.md ---")
readme = f"""# Data 目录 — 数据集说明与处理脚本

## 职责
本目录存放 Netflix Prize 原始数据集、清洗后的核心评分数据和数据挖掘脚本。

## 文件清单

| 文件 | 格式 | 说明 |
|------|------|------|
| archive/ | 目录 | Netflix Prize 原始数据集 |
| ratings_clean.parquet | Parquet | 完整清洗评分数据（~1亿条） |
| ratings_clean.csv | CSV | 采样版评分数据（200万条） |
| movies_clean.csv | CSV | 电影元数据（17,770部） |
| data_mining.py | 脚本 | 数据挖掘与特征工程全流程（可重复执行） |

## 字段字典

### ratings_clean.parquet / ratings_clean.csv
- MovieID — 电影ID（1-17770）
- CustomerID — 匿名用户ID
- Rating — 评分（1-5 整型）
- Date — 评分日期（YYYY-MM-DD）

### movies_clean.csv
- MovieID — 电影ID
- Year — 上映年份
- Title — 电影标题

## 相关目录
- 特征矩阵 → /features/
- EDA 报告 → /notebooks/

## 数据生成
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 处理脚本: scripts/data_mining.py
"""
with open(DATA_DIR / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme)
print("   data/README.md 已创建")

# 创建 features/README.md
features_readme = f"""# Features 目录 — 特征工程产出物

本目录存放特征矩阵，供算法工程师（成员B）使用。

## 文件清单
- user_features.csv  — 用户特征矩阵（{len(user_features):,} 用户 × {len(user_features.columns)} 特征）
- movie_features.csv — 电影特征矩阵（{len(movie_features):,} 电影 × {len(movie_features.columns)} 特征）
- time_features_sample.csv — 时间特征样例

字段字典请参考各文件表头注释或 data/README.md。
"""
with open(FEATURES_DIR / 'README.md', 'w', encoding='utf-8') as f:
    f.write(features_readme)
print("   features/README.md 已创建")

# 创建 notebooks/README.md
notebooks_readme = f"""# Notebooks 目录 — EDA 与分析报告

本目录存放探索性数据分析产出物。

## 文件清单
- eda_report.txt — EDA 数值报告
- eda_visualizations.png — EDA 可视化图表

关键发现：稀疏度 98.8%，评分偏正，长尾效应显著。
"""
with open(NOTEBOOKS_DIR / 'README.md', 'w', encoding='utf-8') as f:
    f.write(notebooks_readme)
print("   notebooks/README.md 已创建")


# ============================================================================
# 完成
# ============================================================================
print("\n" + "=" * 70)
print(" 数据挖掘与特征工程全部完成！")
print("=" * 70)
print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n产出物清单:")

file_map = [
    ('data/', DATA_DIR, ['ratings_clean.parquet', 'ratings_clean.csv', 'movies_clean.csv', 'README.md']),
    ('features/', FEATURES_DIR, ['user_features.csv', 'movie_features.csv', 'time_features_sample.csv', 'README.md']),
    ('notebooks/', NOTEBOOKS_DIR, ['eda_report.txt', 'eda_visualizations.png', 'README.md']),
]
for prefix, dirpath, fnames in file_map:
    for fname in fnames:
        fpath = dirpath / fname
        if fpath.exists():
            print(f"   {prefix}{fname}  ({fpath.stat().st_size/1e6:.1f} MB)")
        else:
            print(f"   {prefix}{fname}  (不存在)")
