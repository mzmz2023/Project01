"""
模型加载器
职责：加载 B 同学训练好的模型文件，提供预测接口。
"""
import pickle
import pandas as pd
from typing import List, Optional

class ModelLoader:
    """加载推荐模型并提供预测方法"""

    def __init__(self, model_path: Optional[str] = None, movies_path: Optional[str] = None):
        self.model_path = model_path
        self.movies_path = movies_path
        self.model = None
        self.movies_df = None

    def load(self):
        """加载模型文件和电影数据"""
        # 加载协同过滤模型
        if self.model_path:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            print("✅ 推荐模型加载成功")
        # 加载电影数据（你现在是 .csv 格式，用 pd.read_csv）
        if self.movies_path:
            self.movies_df = pd.read_csv(self.movies_path)
            print("✅ 电影数据加载成功")

    def predict(self, user_id: int, top_n: int = 20) -> List[dict]:
        """
        对指定用户生成推荐列表
        """
        if self.model is None or self.movies_df is None:
            return []
        
        # 调用模型的推荐方法（按你们同学的模型实现调整）
        # 如果模型的方法名不是 recommend_items，让队友告诉你，我帮你改
        movie_ids = self.model.recommend_items(user_id, top_n)
        
        # 把 movie_id 映射成电影名称
        results = []
        for mid in movie_ids:
            movie_info = self.movies_df[self.movies_df["movie_id"] == mid]
            if not movie_info.empty:
                movie = movie_info.iloc[0]
                results.append({
                    "movie_id": mid,
                    "title": movie["title"],
                    "score": 4.5  # 真实模型会返回score，这里只是示例
                })
        return results

# 全局单例，指定模型路径（和你现在的文件名完全对应）
model_loader = ModelLoader(
    model_path="models/item_cf_model_small.pkl",
    movies_path="models/movies_clean_small.csv"
)