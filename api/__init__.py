from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, text

from server.model_loader import model_loader

router = APIRouter()

# 数据库连接
engine = create_engine("sqlite:///db/recommend.db")

# ---------------------- 公共响应工具 ----------------------
def success(data, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}

def error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}

# ---------------------- 请求/响应模型定义 ----------------------
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

# 响应包装模型（用于 Swagger 文档）
class RecommendListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[RecommendItem] = []

class MovieDetailResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[MovieDetail] = None

class SimilarMoviesResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[RecommendItem] = []

class FeedbackResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: dict = {"status": "received"}

class RefreshResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: dict = {"message": "推荐结果已刷新"}

class StatsOverviewResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[StatsOverview] = None

# ---------------------- 基础接口 ----------------------
@router.get("/")
def root():
    return {"message": "Project01 后端服务运行正常！"}

# ---------------------- 1. 推荐接口 ----------------------
@router.get("/recommend/{user_id}", response_model=RecommendListResponse)
def get_recommendations(user_id: int, top_n: int = 20):
    """获取用户个性化推荐列表"""
    if user_id <= 0:
        return error(1001, "用户不存在")
    try:
        results = model_loader.recommend_items(user_id, top_n)
        return success(data=results)
    except Exception as e:
        return error(5001, f"推荐生成失败：{str(e)}")

# ---------------------- 2. 电影详情接口 ----------------------
@router.get("/movie/{movie_id}", response_model=MovieDetailResponse)
def get_movie_detail(movie_id: int):
    """获取电影元信息"""
    if movie_id <= 0:
        return error(1002, "电影不存在")
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT movie_id, title, genres, year FROM movies WHERE movie_id = :mid"),
                {"mid": movie_id}
            ).fetchone()
        if not row:
            return error(1002, "电影不存在")
        return success(data={
            "movie_id": row[0],
            "title": row[1],
            "genres": row[2],
            "year": row[3],
            "rating": None  # TODO: 从 ratings 表计算平均分
        })
    except Exception as e:
        return error(5001, f"查询失败：{str(e)}")

# ---------------------- 3. 相似电影接口 ----------------------
@router.get("/movie/{movie_id}/similar", response_model=SimilarMoviesResponse)
def get_similar_movies(movie_id: int, top_n: int = 10):
    """获取相似电影推荐"""
    if movie_id <= 0:
        return error(1002, "电影不存在")
    try:
        results = model_loader.get_similar_movies(movie_id, top_n)
        if not results:
            return error(1002, "电影不存在")
        return success(data=results)
    except Exception as e:
        return error(5001, f"相似电影获取失败：{str(e)}")

# ---------------------- 4. 用户反馈接口 ----------------------
@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(feedback: FeedbackRequest):
    """提交用户反馈（喜欢/不感兴趣）"""
    if feedback.user_id <= 0:
        return error(1001, "用户不存在")
    if feedback.action not in ("like", "dislike"):
        return error(2001, "无效的反馈类型，仅支持 like / dislike")
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO ratings (user_id, movie_id, rating, timestamp) "
                     "VALUES (:uid, :mid, :rating, :ts)"),
                {
                    "uid": feedback.user_id,
                    "mid": feedback.movie_id,
                    "rating": 5.0 if feedback.action == "like" else 1.0,
                    "ts": None  # TODO: 补充时间戳
                }
            )
            conn.commit()
        return success(data={"status": "received"})
    except Exception as e:
        return error(5001, f"反馈提交失败：{str(e)}")

# ---------------------- 5. 刷新推荐接口 ----------------------
@router.post("/refresh/{user_id}", response_model=RefreshResponse)
def refresh_recommendations(user_id: int):
    """刷新用户推荐结果"""
    if user_id <= 0:
        return error(1001, "用户不存在")
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM rec_cache WHERE user_id = :uid"), {"uid": user_id})
            conn.commit()
        return success(data={"message": "推荐结果已刷新"})
    except Exception as e:
        return error(5001, f"刷新失败：{str(e)}")

# ---------------------- 6. 系统概况接口 ----------------------
@router.get("/stats/overview", response_model=StatsOverviewResponse)
def get_stats_overview():
    """系统概况数据（仪表盘用）"""
    try:
        with engine.connect() as conn:
            users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
            movies = conn.execute(text("SELECT COUNT(*) FROM movies")).scalar() or 0
            ratings = conn.execute(text("SELECT COUNT(*) FROM ratings")).scalar() or 0
            avg = conn.execute(text("SELECT AVG(rating) FROM ratings")).scalar() or 0
        return success(data={
            "total_users": users,
            "total_movies": movies,
            "total_ratings": ratings,
            "avg_rating": round(float(avg), 2)
        })
    except Exception as e:
        return error(5001, f"统计查询失败：{str(e)}")
