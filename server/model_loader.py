"""
模型加载器

职责：加载 B 同学训练好的模型文件，提供预测接口。
当前为占位实现，待模型就绪后替换。
"""

from typing import List, Optional


class ModelLoader:
    """加载推荐模型并提供预测方法"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None

    def load(self):
        """加载模型文件（待实现）"""
        if self.model_path:
            # TODO: 从 self.model_path 加载模型
            # 示例：self.model = pickle.load(open(self.model_path, "rb"))
            pass

    def predict(self, user_id: int, top_n: int = 20) -> List[dict]:
        """
        对指定用户生成推荐列表

        参数:
            user_id: 用户 ID
            top_n: 返回数量

        返回:
            [{"movie_id": int, "title": str, "score": float}, ...]
        """
        # TODO: 调用 self.model 进行预测，替换 mock 数据
        return []


# 全局单例
model_loader = ModelLoader()
