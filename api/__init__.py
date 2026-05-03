from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

# 初始化路由
router = APIRouter()

# ---------------------- 数据模型定义 ----------------------
class RecommendRequest(BaseModel):
    user_id: int
    context: Optional[dict] = None

class RecommendItem(BaseModel):
    movie_id: int
    title: str
    score: Optional[float] = None

class RecommendResponse(BaseModel):
    code: int
    message: str
    data: List[RecommendItem]

# ---------------------- 基础接口 ----------------------
@router.get("/")
def root():
    return {"message": "Project01 后端服务运行正常！"}

# ---------------------- 推荐接口（纯示例，无数据库） ----------------------
@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
    # 直接返回固定示例数据，后续模型训练好后再替换
    return {
        "code": 200,
        "message": "success",
        "data": [
            {"movie_id": 1, "title": "示例高分电影1", "score": 4.8},
            {"movie_id": 2, "title": "示例高分电影2", "score": 4.5},
            {"movie_id": 3, "title": "示例高分电影3", "score": 4.3}
        ]
    }