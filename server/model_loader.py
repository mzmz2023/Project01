"""
模型加载器
职责：加载 B 同学训练好的模型文件，提供推荐 / 相似电影接口。
"""
import pickle
import pandas as pd
from typing import List, Optional


class ModelLoader:
    """加载推荐模型并提供推荐方法"""

    def __init__(self, model_path: Optional[str] = None, movies_path: Optional[str] = None):
        self.model_path = model_path
        self.movies_path = movies_path
        self.model = None
        self.movies_df = None

    def load(self):
        """加载模型文件和电影数据"""
        if self.model_path:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            print("✅ 推荐模型加载成功")
        if self.movies_path:
            self.movies_df = pd.read_csv(self.movies_path)
            print("✅ 电影数据加载成功")

    def recommend_items(self, user_id: int, top_n: int = 20) -> List[dict]:
        """
        对指定用户生成推荐列表
        基于 ItemCF 相似度矩阵：找到用户高分电影的相似电影，加权聚合后排 top_n
        """
        if self.model is None or self.movies_df is None:
            return []

        sim = self.model.get('sim')
        ratings = self.model.get('ratings')
        if sim is None or ratings is None:
            print("⚠️ 模型文件格式异常：缺少 'sim' 或 'ratings' 字段")
            return []

        # 冷启动：用户无评分记录
        if user_id not in ratings:
            return []

        user_ratings = ratings[user_id]
        # 取用户评分 >= 4 的电影作为种子
        seed_movies = [mid for mid, r in user_ratings.items() if r >= 4]
        if not seed_movies:
            seed_movies = list(user_ratings.keys())

        # 加权聚合候选电影得分
        scores = {}
        for mid in seed_movies:
            if mid not in sim.index:
                continue
            # 取每个种子电影最相似的 50 部
            similar = sim[mid].sort_values(ascending=False)[1:51]
            for sim_mid, sim_val in similar.items():
                if sim_mid in user_ratings:
                    continue  # 已评分，跳过
                scores[sim_mid] = scores.get(sim_mid, 0) + sim_val * user_ratings[mid]

        # 按得分降序排列
        sorted_items = sorted(scores.items(), key=lambda x: -x[1])

        # 组装结果
        results = []
        for mid, score in sorted_items[:top_n]:
            title = "未知电影"
            match = self.movies_df[self.movies_df["MovieID"] == mid]
            if not match.empty:
                title = match.iloc[0].get("Title", "未知电影")
            results.append({
                "movie_id": int(mid),
                "title": title,
                "score": round(float(score), 4)
            })
        return results

    def get_similar_movies(self, movie_id: int, top_n: int = 10) -> List[dict]:
        """获取某部电影的相似电影"""
        if self.model is None or self.movies_df is None:
            return []

        sim = self.model.get('sim')
        if sim is None:
            print("⚠️ 模型文件格式异常：缺少 'sim' 字段")
            return []
        if movie_id not in sim.index:
            return []

        similar = sim[movie_id].sort_values(ascending=False)[1:top_n + 1]
        results = []
        for mid, val in similar.items():
            title = "未知电影"
            match = self.movies_df[self.movies_df["MovieID"] == mid]
            if not match.empty:
                title = match.iloc[0].get("Title", "未知电影")
            results.append({
                "movie_id": int(mid),
                "title": title,
                "score": round(float(val), 4)
            })
        return results


# 全局单例
model_loader = ModelLoader(
    model_path="models/item_cf_model_small.pkl",
    movies_path="models/movies_clean_small.csv"
)
