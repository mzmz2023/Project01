# -*- coding: utf-8 -*-
"""
Netflix Prize 推荐算法（双数据集版本：小样本+全量 独立训练保存）
功能说明：实现ItemCF（基于物品的协同过滤）和ALS（交替最小二乘矩阵分解）两种推荐算法，
         支持小样本CSV和全量Parquet数据集独立训练、评估、保存
"""

# ===================== 【1. 导入依赖库】 =====================
# 数据处理相关
import pandas as pd
import numpy as np
# 模型保存与文件操作
import pickle
import os
# 时间处理
import time
# 可视化
import matplotlib.pyplot as plt
# 机器学习工具
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
# 进度条
from tqdm import tqdm
# 稀疏矩阵计算
import scipy.sparse as sp
from scipy.sparse.linalg import norm
# 深度学习框架
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# ===================== 【2. 全局配置】 =====================
# 解决matplotlib中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 自动检测计算设备（GPU/CPU）
print("=" * 50)
print("【系统初始化】检查计算设备...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == 'cuda':
    print(f"✅ 检测到GPU：{torch.cuda.get_device_name(0)}")
else:
    print("⚠️  未检测到GPU，使用CPU运行（训练会较慢）")
print(f"当前使用设备：{device}")
print("=" * 50)
time.sleep(1)  # 暂停1秒，方便查看设备信息


# ===================== 【3. 数据加载与预处理函数】 =====================
def load_data(data_path):
    """
    加载并预处理评分数据和电影数据
    参数：
        data_path: 评分数据文件路径（支持.csv/.parquet）
    返回：
        df_movies: 电影信息数据框
        train_data: 训练集数据
        val_data: 验证集数据
        test_data: 测试集数据
        id_mappings: ID映射字典（用户/电影ID与索引的双向映射）
    """
    print("\n" + "=" * 50)
    print("【数据加载与预处理】")
    print("=" * 50)

    # 加载评分数据（自动识别文件格式）
    print("\n正在加载数据...")
    if data_path.endswith('.csv'):
        df_ratings = pd.read_csv(data_path)
    elif data_path.endswith('.parquet'):
        df_ratings = pd.read_parquet(data_path, engine='pyarrow')
    else:
        raise ValueError("不支持的数据格式！仅支持.csv和.parquet")

    # 加载电影信息数据
    df_movies = pd.read_csv('data/movies_clean.csv')

    # 打印数据基本信息
    print("\n【数据基本信息】")
    print(f"评分数据量：{len(df_ratings)}")
    print(f"用户数：{df_ratings['CustomerID'].nunique()}")
    print(f"电影数：{df_ratings['MovieID'].nunique()}")

    # 过滤低频用户和电影（减少数据量、加速训练、降低噪声）
    print("\n正在过滤低频用户和电影...")
    user_counts = df_ratings['CustomerID'].value_counts()
    movie_counts = df_ratings['MovieID'].value_counts()
    active_users = user_counts[user_counts >= 5].index
    active_movies = movie_counts[movie_counts >= 10].index
    df_ratings = df_ratings[
        df_ratings['CustomerID'].isin(active_users) &
        df_ratings['MovieID'].isin(active_movies)
    ]
    print(f"过滤后数据量：{len(df_ratings)}")
    print(f"用户数：{df_ratings['CustomerID'].nunique()}")
    print(f"电影数：{df_ratings['MovieID'].nunique()}")

    # 重新编码用户/电影ID为连续索引（方便模型计算）
    print("\n正在重新编码ID...")
    user_ids = df_ratings['CustomerID'].unique()
    movie_ids = df_ratings['MovieID'].unique()
    # 用户ID→索引映射
    user_id_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    # 电影ID→索引映射
    movie_id_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
    # 反向映射（索引→原始ID）
    idx_to_user_id = {i: uid for uid, i in user_id_to_idx.items()}
    idx_to_movie_id = {i: mid for mid, i in movie_id_to_idx.items()}

    # 添加编码后的索引列到数据框
    df_ratings['user_idx'] = df_ratings['CustomerID'].map(user_id_to_idx)
    df_ratings['movie_idx'] = df_ratings['MovieID'].map(movie_id_to_idx)

    # 划分训练集/测试集/验证集（80%训练，16%测试，4%验证）
    print("\n正在划分训练集/测试集/验证集...")
    train_data, test_data = train_test_split(df_ratings, test_size=0.2, random_state=42)
    train_data, val_data = train_test_split(train_data, test_size=0.05, random_state=42)

    # 整理ID映射字典
    id_mappings = {
        'user_id_to_idx': user_id_to_idx,
        'movie_id_to_idx': movie_id_to_idx,
        'idx_to_user_id': idx_to_user_id,
        'idx_to_movie_id': idx_to_movie_id
    }

    return df_movies, train_data, val_data, test_data, id_mappings


# ===================== 【4. 基于物品的协同过滤（ItemCF）类】 =====================
class ItemCF:
    """
    基于物品的协同过滤推荐算法类
    核心思想：计算物品（电影）之间的相似度，基于用户对相似物品的评分预测目标物品评分
    """

    def __init__(self, train_data):
        """
        初始化函数
        参数：
            train_data: 训练集数据框（包含CustomerID/MovieID/Rating列）
        """
        self.train_data = train_data  # 训练数据
        self.movie_similarity = None  # 电影相似度矩阵
        self.user_movie_ratings = None  # 用户-电影评分字典
        self.movie2idx = {}  # 电影ID→索引映射
        self.idx2movie = {}  # 索引→电影ID映射
        self.user2idx = {}  # 用户ID→索引映射

    def fit(self):
        """
        训练ItemCF模型：构建评分字典、ID映射、稀疏矩阵，计算电影相似度
        """
        print("\n" + "=" * 50)
        print("【任务 2】基于物品的协同过滤（ItemCF）实现")
        print("=" * 50)
        print("\n【ItemCF训练开始】")

        # 构建用户-电影评分字典（key:用户ID, value: {电影ID: 评分}）
        print("正在构建用户-电影评分字典...")
        self.user_movie_ratings = {}
        for _, row in tqdm(self.train_data.iterrows(), total=len(self.train_data), desc="构建字典"):
            user_id = row['CustomerID']
            movie_id = row['MovieID']
            rating = row['Rating']
            if user_id not in self.user_movie_ratings:
                self.user_movie_ratings[user_id] = {}
            self.user_movie_ratings[user_id][movie_id] = rating

        # 构建电影/用户ID与索引的映射
        print("正在构建ID映射表...")
        unique_movies = self.train_data['MovieID'].unique()
        for idx, movie_id in enumerate(unique_movies):
            self.movie2idx[movie_id] = idx
            self.idx2movie[idx] = movie_id
        unique_users = self.train_data['CustomerID'].unique()
        for idx, user_id in enumerate(unique_users):
            self.user2idx[user_id] = idx

        # 构建电影-用户稀疏评分矩阵（行：电影，列：用户，值：评分）
        print("正在构建稀疏电影-用户评分矩阵...")
        data = []  # 评分值列表
        row_ind = []  # 电影索引列表
        col_ind = []  # 用户索引列表
        for _, row in self.train_data.iterrows():
            movie_idx = self.movie2idx[row['MovieID']]
            user_idx = self.user2idx[row['CustomerID']]
            data.append(row['Rating'])
            row_ind.append(movie_idx)
            col_ind.append(user_idx)
        # 构建CSR格式稀疏矩阵（节省内存，提高计算效率）
        movie_user_sparse = sp.csr_matrix(
            (data, (row_ind, col_ind)),
            shape=(len(unique_movies), len(unique_users))
        )

        # 计算电影相似度矩阵（余弦相似度）
        print("正在计算电影相似度矩阵...")
        # 计算每个电影向量的范数（用于余弦相似度分母）
        movie_norms = norm(movie_user_sparse, axis=1)
        movie_norms[movie_norms == 0] = 1e-8  # 避免除以0
        # 稀疏矩阵相乘（计算分子部分）
        similarity = movie_user_sparse @ movie_user_sparse.T
        similarity = similarity.toarray()  # 转为密集矩阵

        # 归一化得到余弦相似度
        for i in tqdm(range(similarity.shape[0]), desc="计算余弦相似度"):
            for j in range(similarity.shape[1]):
                similarity[i][j] /= (movie_norms[i] * movie_norms[j])

        # 转换为DataFrame（方便索引和查询）
        self.movie_similarity = pd.DataFrame(similarity, index=unique_movies, columns=unique_movies)
        print("【ItemCF训练完成】")

    def predict(self, user_id, movie_id):
        """
        预测用户对指定电影的评分
        参数：
            user_id: 用户ID
            movie_id: 电影ID
        返回：
            pred_rating: 预测评分（1-5分）
        """
        # 若用户无评分记录，返回默认评分3.0
        if user_id not in self.user_movie_ratings:
            return 3.0
        user_rated_movies = self.user_movie_ratings[user_id]

        # 若电影无相似度数据，返回用户平均评分
        if movie_id not in self.movie_similarity.index:
            return np.mean(list(user_rated_movies.values()))

        # 取相似度最高的前10个相似电影（排除自身）
        similar_movies = self.movie_similarity[movie_id].sort_values(ascending=False)[1:11]
        weighted_sum = 0.0  # 加权评分和
        similarity_sum = 0.0  # 相似度和

        # 计算加权平均评分
        for sim_movie_id, sim in similar_movies.items():
            if sim_movie_id in user_rated_movies:
                weighted_sum += sim * user_rated_movies[sim_movie_id]
                similarity_sum += sim

        # 若没有相似电影评分，返回用户平均评分；否则返回加权平均
        return weighted_sum / similarity_sum if similarity_sum != 0 else np.mean(list(user_rated_movies.values()))


# ===================== 【5. ALS矩阵分解模型相关】 =====================
class RatingDataset(Dataset):
    """
    PyTorch数据集类：封装评分数据，适配DataLoader
    """

    def __init__(self, data):
        """
        初始化数据集
        参数：
            data: 包含user_idx/movie_idx/Rating列的数据框
        """
        self.user_indices = torch.tensor(data['user_idx'].values, dtype=torch.long)  # 用户索引（长整型）
        self.movie_indices = torch.tensor(data['movie_idx'].values, dtype=torch.long)  # 电影索引（长整型）
        self.ratings = torch.tensor(data['Rating'].values, dtype=torch.float32)  # 评分（浮点型）

    def __len__(self):
        """返回数据集总长度"""
        return len(self.ratings)

    def __getitem__(self, idx):
        """获取指定索引的样本（用户索引、电影索引、评分）"""
        return self.user_indices[idx], self.movie_indices[idx], self.ratings[idx]


class ALSModel(nn.Module):
    """
    ALS矩阵分解模型（PyTorch实现）
    模型结构：用户嵌入 + 电影嵌入 + 用户偏置 + 电影偏置 + 全局偏置
    """

    def __init__(self, num_users, num_movies, n_factors=128):
        """
        初始化模型
        参数：
            num_users: 用户总数
            num_movies: 电影总数
            n_factors: 嵌入维度（默认128）
        """
        super().__init__()
        # 用户嵌入层（每个用户映射为n_factors维向量）
        self.user_factors = nn.Embedding(num_users, n_factors)
        # 电影嵌入层（每个电影映射为n_factors维向量）
        self.movie_factors = nn.Embedding(num_movies, n_factors)
        # 用户偏置项（每个用户的评分偏置）
        self.user_bias = nn.Embedding(num_users, 1)
        # 电影偏置项（每个电影的评分偏置）
        self.movie_bias = nn.Embedding(num_movies, 1)
        # 全局偏置项（整体评分基准）
        self.global_bias = nn.Parameter(torch.tensor(0.0))

        # 初始化嵌入层权重（正态分布）
        nn.init.normal_(self.user_factors.weight, std=0.01)
        nn.init.normal_(self.movie_factors.weight, std=0.01)

    def forward(self, user_indices, movie_indices):
        """
        前向传播：计算预测评分
        参数：
            user_indices: 用户索引张量
            movie_indices: 电影索引张量
        返回：
            pred_ratings: 预测评分张量
        """
        # 获取用户和电影嵌入向量
        user_emb = self.user_factors(user_indices)
        movie_emb = self.movie_factors(movie_indices)
        # 计算预测评分：全局偏置 + 用户偏置 + 电影偏置 + 嵌入向量点积
        return (self.global_bias +
                self.user_bias(user_indices).squeeze() +
                self.movie_bias(movie_indices).squeeze() +
                (user_emb * movie_emb).sum(dim=1))


class ALSRecommender:
    """
    ALS推荐器：封装模型训练、评估、预测逻辑
    """

    def __init__(self, train_data, val_data, id_mappings, n_factors=64, lr=0.002, epochs=15, batch_size=16384):
        """
        初始化ALS推荐器
        参数：
            train_data: 训练集数据
            val_data: 验证集数据
            id_mappings: ID映射字典
            n_factors: 嵌入维度（默认128）
            lr: 学习率（默认0.001）
            epochs: 训练轮数（默认25）
            batch_size: 批次大小（默认8192）
        """
        self.train_data = train_data  # 训练数据
        self.val_data = val_data  # 验证数据
        self.id_mappings = id_mappings  # ID映射
        self.n_factors = n_factors  # 嵌入维度
        self.lr = lr  # 学习率
        self.epochs = epochs  # 训练轮数
        self.batch_size = batch_size  # 批次大小
        self.model = None  # ALS模型实例
        self.train_rmse_list = []  # 训练集RMSE记录
        self.val_rmse_list = []  # 验证集RMSE记录

    def evaluate_val(self, val_dataloader, criterion):
        """
        评估验证集RMSE
        参数：
            val_dataloader: 验证集数据加载器
            criterion: 损失函数（MSELoss）
        返回：
            val_rmse: 验证集RMSE值
        """
        self.model.eval()  # 切换到评估模式（关闭Dropout/BatchNorm等）
        total_loss = 0.0
        with torch.no_grad():  # 禁用梯度计算（节省内存，加快速度）
            for user, movie, rating in val_dataloader:
                # 预测评分（将数据移到指定设备）
                pred = self.model(user.to(device), movie.to(device))
                # 计算损失
                total_loss += criterion(pred, rating.to(device)).item()
        # RMSE = sqrt(MSE)
        return np.sqrt(total_loss / len(val_dataloader))

    def plot_rmse_curve(self, save_name):
        """
        绘制训练/验证集RMSE变化曲线并保存
        参数：
            save_name: 图片保存路径/名称
        """
        plt.figure(figsize=(10, 5))
        # 绘制训练集RMSE曲线
        plt.plot(self.train_rmse_list, label='训练集RMSE', linewidth=2)
        # 绘制验证集RMSE曲线
        plt.plot(self.val_rmse_list, label='验证集RMSE', linewidth=2)
        # 图表样式设置
        plt.title('ALS模型 RMSE变化曲线', fontsize=14)
        plt.xlabel('训练轮数 (Epoch)', fontsize=12)
        plt.ylabel('RMSE 值', fontsize=12)
        plt.legend()  # 显示图例
        plt.grid(True, alpha=0.3)  # 显示网格（透明度0.3）
        # 保存图片（高分辨率，裁剪空白）
        plt.savefig(save_name, dpi=300, bbox_inches='tight')
        plt.close()  # 关闭画布（释放内存）
        print(f"✅ RMSE曲线已保存：{save_name}")

    def fit(self):
        """
        训练ALS模型：包含早停、学习率调度、RMSE监控
        """
        print("\n" + "=" * 50)
        print("【任务 3】ALS模型训练")
        print("=" * 50)
        print("\n【ALS训练开始】")

        # 获取用户/电影总数
        num_users = len(self.id_mappings['user_id_to_idx'])
        num_movies = len(self.id_mappings['movie_id_to_idx'])

        # 初始化模型并移到指定设备
        self.model = ALSModel(num_users, num_movies, self.n_factors).to(device)
        # 损失函数：均方误差（MSE）
        criterion = nn.MSELoss()
        # 优化器：Adam（带权重衰减，防止过拟合）
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-5)
        # 学习率调度器：验证集RMSE停止下降时，学习率减半（耐心值2）
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=2, factor=0.5)

        # 创建数据加载器
        train_loader = DataLoader(RatingDataset(self.train_data), batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(RatingDataset(self.val_data), batch_size=self.batch_size)

        # 早停相关参数
        best_val_rmse = float('inf')  # 最佳验证集RMSE（初始化为无穷大）
        early_stop_count = 0  # 早停计数器

        # 开始训练
        for epoch in range(self.epochs):
            self.model.train()  # 切换到训练模式
            total_loss = 0.0
            # 进度条显示训练进度
            progress_bar = tqdm(train_loader, desc=f"Epoch [{epoch + 1}/{self.epochs}]")

            # 批次训练
            for user, movie, rating in progress_bar:
                optimizer.zero_grad()  # 清空梯度
                # 预测评分
                pred = self.model(user.to(device), movie.to(device))
                # 计算损失
                loss = criterion(pred, rating.to(device))
                # 反向传播
                loss.backward()
                # 更新参数
                optimizer.step()
                # 累计损失
                total_loss += loss.item()
                # 进度条显示当前批次RMSE
                progress_bar.set_postfix({'RMSE': f'{torch.sqrt(loss).item():.4f}'})

            # 计算本轮训练集RMSE
            train_rmse = np.sqrt(total_loss / len(train_loader))
            # 计算本轮验证集RMSE
            val_rmse = self.evaluate_val(val_loader, criterion)
            # 记录RMSE
            self.train_rmse_list.append(train_rmse)
            self.val_rmse_list.append(val_rmse)

            # 更新学习率
            scheduler.step(val_rmse)
            # 打印本轮训练结果
            print(f"✅ Epoch {epoch + 1} | 训练RMSE: {train_rmse:.4f} | 验证RMSE: {val_rmse:.4f}")

            # 早停逻辑：验证集RMSE未提升时计数，累计3轮则停止训练
            if val_rmse < best_val_rmse:
                best_val_rmse = val_rmse
                early_stop_count = 0
            else:
                early_stop_count += 1
                if early_stop_count >= 2:
                    print("🛑 早停触发：防止过拟合")
                    break

        print("【ALS训练完成】")

    def predict(self, user_id, movie_id):
        """
        预测用户对指定电影的评分
        参数：
            user_id: 用户ID
            movie_id: 电影ID
        返回：
            pred_rating: 预测评分（限制在1-5分之间）
        """
        # 获取用户/电影索引（无则返回0）
        user_idx = self.id_mappings['user_id_to_idx'].get(user_id, 0)
        movie_idx = self.id_mappings['movie_id_to_idx'].get(movie_id, 0)

        # 禁用梯度计算，预测评分
        with torch.no_grad():
            pred = self.model(torch.tensor([user_idx]).to(device), torch.tensor([movie_idx]).to(device))
            # 限制评分在1-5分之间
            pred_clamped = torch.clamp(pred, 1, 5)
            return float(pred_clamped)


# ===================== 【6. 模型评估函数】 =====================
def calculate_rmse(model, test_data, model_type):
    """
    计算模型在测试集上的RMSE（随机采样10万条数据，加快评估速度）
    参数：
        model: 待评估模型（ItemCF/ALS）
        test_data: 测试集数据
        model_type: 模型名称（用于打印日志）
    返回：
        rmse: 测试集RMSE值
    """
    predictions = []  # 预测评分列表
    true_ratings = []  # 真实评分列表

    # 随机采样10万条数据（避免全量评估耗时过长）
    test_sample = test_data.sample(n=100000, random_state=42)

    # 批量预测
    for _, row in tqdm(test_sample.iterrows(), total=len(test_sample), desc=f"评估{model_type}"):
        pred = model.predict(row['CustomerID'], row['MovieID'])
        predictions.append(pred)
        true_ratings.append(row['Rating'])

    # 计算RMSE
    rmse = np.sqrt(np.mean((np.array(predictions) - true_ratings) ** 2))
    print(f"{model_type} 测试集RMSE: {rmse:.4f}")
    return rmse


# ===================== 【7. 模型保存函数】 =====================
def save_model_files(item_cf, als, df_movies, save_folder):
    """
    保存模型文件、ID映射、电影信息
    参数：
        item_cf: 训练好的ItemCF模型
        als: 训练好的ALS推荐器
        df_movies: 电影信息数据框
        save_folder: 保存文件夹路径
    """
    # 创建文件夹（不存在则创建）
    os.makedirs(save_folder, exist_ok=True)

    # 保存ItemCF模型（相似度矩阵 + 评分字典）
    with open(f'{save_folder}/item_cf_model.pkl', 'wb') as f:
        pickle.dump({
            'sim': item_cf.movie_similarity,
            'ratings': item_cf.user_movie_ratings
        }, f)

    # 保存ALS模型（模型参数 + ID映射）
    torch.save({
        'model': als.model.cpu().state_dict(),  # 移到CPU再保存（兼容无GPU环境）
        'mapping': als.id_mappings
    }, f'{save_folder}/als_model.pth')

    # 保存电影信息
    df_movies.to_csv(f'{save_folder}/movies_clean.csv', index=False)

    print(f"\n✅ 模型已保存至文件夹：{save_folder}")


# ===================== 【8. 核心训练流程函数】 =====================
def train_and_save(data_path, save_folder):
    """
    端到端训练流程：加载数据 → 训练ItemCF → 训练ALS → 评估 → 保存模型
    参数：
        data_path: 数据文件路径
        save_folder: 模型保存文件夹
    """
    # 步骤1：加载并预处理数据
    df_movies, train_data, val_data, test_data, id_mappings = load_data(data_path)

    # 步骤2：训练ItemCF模型
    item_cf = ItemCF(train_data)
    item_cf.fit()

    # 步骤3：训练ALS模型
    als = ALSRecommender(train_data, val_data, id_mappings)
    als.fit()
    # 保存RMSE曲线（区分不同数据集）
    als.plot_rmse_curve(f'RMSE_{save_folder}.png')

    # 步骤4：模型评估（对比ItemCF和ALS）
    print("\n" + "=" * 50)
    print(f"【{save_folder} 模型对比】")
    calculate_rmse(item_cf, test_data, "ItemCF")
    calculate_rmse(als, test_data, "ALS")
    print("=" * 50)

    # 步骤5：保存模型文件
    save_model_files(item_cf, als, df_movies, save_folder)


# ===================== 【9. 主程序入口】 =====================
if __name__ == "__main__":
    """
    主程序：依次训练小样本CSV数据和全量Parquet数据
    """
    # 第一步：训练小样本CSV数据（ratings_clean.csv）
    print("\n" + "=" * 50)
    print("🚀 开始训练：小样本数据 (ratings_clean.csv)")
    print("=" * 50)
    train_and_save(
        data_path='data/ratings_clean.csv',
        save_folder='models_small_csv'  # 小样本模型保存文件夹
    )

    # 第二步：训练全量Parquet数据（ratings_clean.parquet）
    print("\n" + "=" * 50)
    print("🚀 开始训练：全量数据 (ratings_clean.parquet)")
    print("=" * 50)
    train_and_save(
        data_path='data/ratings_clean.parquet',
        save_folder='models_full_parquet'  # 全量模型保存文件夹
    )

    # 训练完成提示
    print("\n🎉 所有数据集训练完成！模型已分别保存！") 