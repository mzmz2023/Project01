from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# ---------------------- 1. 跨域配置（彻底解决CORS问题） ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- 2. 公共响应工具 ----------------------
def success(data, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}

def error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}

# ---------------------- 3. 数据模型定义 ----------------------
class RecommendItem(BaseModel):
    movie_id: int
    title: str
    score: Optional[float] = None
    poster: Optional[str] = None
    reason: Optional[str] = None

class FeedbackRequest(BaseModel):
    user_id: int
    movie_id: int
    action: str

# ---------------------- 4. 所有接口（直接写在main.py里，不会再404） ----------------------
# 基础接口
@app.get("/api/")
def root():
    return {"message": "Project01 后端服务运行正常！"}

# 推荐接口
@app.get("/api/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = 20):
    if user_id <= 0:
        return error(1001, "用户不存在")

    test_data = [
        {"movie_id": 1, "title": "流浪地球", "score": 9.0, "poster": "", "reason": "科幻推荐"},
        {"movie_id": 2, "title": "满江红", "score": 8.5, "poster": "", "reason": "悬疑推荐"},
        {"movie_id": 3, "title": "哪吒之魔童降世", "score": 8.8, "poster": "", "reason": "动画推荐"}
    ]
    return success(data=test_data)

# 刷新推荐接口
@app.post("/api/refresh/{user_id}")
def refresh_recommendations(user_id: int, top_n: int = 20):
    if user_id <= 0:
        return error(1001, "用户不存在")

    test_data = [
        {"movie_id": 1, "title": "流浪地球", "score": 9.0, "poster": "", "reason": "科幻推荐"},
        {"movie_id": 2, "title": "满江红", "score": 8.5, "poster": "", "reason": "悬疑推荐"},
        {"movie_id": 3, "title": "哪吒之魔童降世", "score": 8.8, "poster": "", "reason": "动画推荐"}
    ]
    return success(data={"status": "refreshed", "recommendations": test_data})

# 电影详情接口
@app.get("/api/movie/{movie_id}")
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

# 相似电影接口
@app.get("/api/movie/{movie_id}/similar")
def get_similar(movie_id: int, top_n: int = 10):
    if movie_id <= 0:
        return error(1002, "电影不存在")

    test_data = [
        {"movie_id": 4, "title": "星际穿越", "score": 9.2, "poster": "", "reason": "同类型推荐"},
        {"movie_id": 5, "title": "盗梦空间", "score": 9.3, "poster": "", "reason": "同类型推荐"}
    ]
    return success(data=test_data)

# 用户反馈接口
@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackRequest):
    if feedback.user_id <= 0 or feedback.movie_id <= 0:
        return error(1003, "参数无效")
    return success(data={"status": "received"})

# 统计概览接口
@app.get("/api/stats/overview")
def get_stats():
    return success(data={
        "total_users": 1000,
        "total_movies": 5000,
        "total_ratings": 100000,
        "avg_rating": 3.8
    })