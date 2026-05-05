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
    action: str

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
    if user_id <= 0:
        return error(1001, "用户不存在")

    # ✅【只改这里】导入放进函数内 + 自动加载模型
    from server.model_loader import model_loader
    model_loader.load()  # <--- 自动加载

    result = model_loader.recommend_items(user_id=user_id, top_n=top_n)
    return success(data=result)

# ---------------------- 2. 电影详情接口 ----------------------
@router.get("/movie/{movie_id}")
def get_movie_detail(movie_id: int):
    if movie_id <= 0:
        return error(1002, "电影不存在")
    return success(data={
        "movie_id": movie_id,
        "title": "示例电影",
        "genres": "Action|Drama",
        "year": 2020,
        "rating": 4.5
    })

# ---------------------- 3. 相似电影接口 ----------------------
@router.get("/movie/{movie_id}/similar")
def get_similar(movie_id: int, top_n: int = 10):
    if movie_id <= 0:
        return error(1002, "电影不存在")

    # ✅【只改这里】导入放进函数内 + 自动加载模型
    from server.model_loader import model_loader
    model_loader.load()  # <--- 自动加载

    result = model_loader.get_similar_movies(movie_id=movie_id, top_n=top_n)
    return success(data=result)

# ---------------------- 4. 用户反馈接口 ----------------------
@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    if feedback.user_id <= 0 or feedback.movie_id <= 0:
        return error(1003, "参数无效")
    return success(data={"status": "received"})

# ---------------------- 5. 统计概览接口 ----------------------
@router.get("/stats/overview")
def get_stats():
    return success(data={
        "total_users": 1000,
        "total_movies": 5000,
        "total_ratings": 100000,
        "avg_rating": 3.8
    })