from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# ---------------------- 公共响应工具 ----------------------
def success(data, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}

def error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}

# ---------------------- 数据模型定义 ----------------------
class RecommendItem(BaseModel):
    movie_id: int
    title: str
    score: Optional[float] = None
    poster: Optional[str] = None
    reason: Optional[str] = None

class MovieDetail(BaseModel):
    movie_id: int
    title: str
    genres: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None

class FeedbackRequest(BaseModel):
    user_id: int
    movie_id: int
    action: str  # "like" 或 "dislike"

class StatsOverview(BaseModel):
    total_users: int
    total_movies: int
    total_ratings: int
    avg_rating: float

# ---------------------- 基础接口 ----------------------
@router.get("/")
def root():
    return {"message": "Project01 后端服务运行正常！"}

# ---------------------- 1. 推荐接口 ----------------------
@router.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = 20):
    """获取用户个性化推荐列表"""
    if user_id <= 0:
        return error(1001, "用户不存在")
    # TODO: 替换为真实模型预测结果
    mock_data = [
        {"movie_id": 1, "title": "示例高分电影1", "score": 4.8},
        {"movie_id": 2, "title": "示例高分电影2", "score": 4.5},
        {"movie_id": 3, "title": "示例高分电影3", "score": 4.3},
        {"movie_id": 4, "title": "示例高分电影4", "score": 4.1},
        {"movie_id": 5, "title": "示例高分电影5", "score": 3.9},
    ]
    return success(data=mock_data[:top_n])

# ---------------------- 2. 电影详情接口 ----------------------
@router.get("/movie/{movie_id}")
def get_movie_detail(movie_id: int):
    """获取电影元信息"""
    if movie_id <= 0:
        return error(1002, "电影不存在")
    # TODO: 从数据库查询真实数据
    return success(data={
        "movie_id": movie_id,
        "title": "示例电影",
        "genres": "Action|Drama",
        "year": 2020,
        "rating": 4.5
    })

# ---------------------- 3. 相似电影接口 ----------------------
@router.get("/movie/{movie_id}/similar")
def get_similar_movies(movie_id: int, top_n: int = 10):
    """获取相似电影推荐"""
    if movie_id <= 0:
        return error(1002, "电影不存在")
    # TODO: 从模型/数据库查询相似电影
    return success(data=[
        {"movie_id": 101, "title": "相似电影1", "score": 4.2},
        {"movie_id": 102, "title": "相似电影2", "score": 4.0},
    ][:top_n])

# ---------------------- 4. 用户反馈接口 ----------------------
@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """提交用户反馈（喜欢/不感兴趣）"""
    if feedback.user_id <= 0:
        return error(1001, "用户不存在")
    if feedback.action not in ("like", "dislike"):
        return error(2001, "无效的反馈类型，仅支持 like / dislike")
    # TODO: 保存到数据库
    return success(data={"status": "received"})

# ---------------------- 5. 刷新推荐接口 ----------------------
@router.post("/refresh/{user_id}")
def refresh_recommendations(user_id: int):
    """刷新用户推荐结果"""
    if user_id <= 0:
        return error(1001, "用户不存在")
    # TODO: 触发模型重新预测并更新缓存
    return success(data={"message": "推荐结果已刷新"})

# ---------------------- 6. 系统概况接口 ----------------------
@router.get("/stats/overview")
def get_stats_overview():
    """系统概况数据（仪表盘用）"""
    # TODO: 从数据库统计真实数据
    return success(data={
        "total_users": 1000,
        "total_movies": 5000,
        "total_ratings": 100000,
        "avg_rating": 3.8
    })