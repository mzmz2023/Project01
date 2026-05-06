from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np

# 导入我们刚写好的推荐函数
from scripts.recommendation_system_1 import load_trained_model

app = FastAPI()

# ---------------------- 0. 服务启动时预加载模型（性能优化） ----------------------
# 全局变量，存储加载好的模型和数据
item_cf_data = None
als_model_data = None
df_movies = None
movie_sim_matrix = None
user_rated_dict = None

@app.on_event("startup")
async def startup_event():
    """服务启动时自动执行，预加载模型到内存"""
    global item_cf_data, als_model_data, df_movies, movie_sim_matrix, user_rated_dict
    print("正在预加载推荐模型，请稍候...")
    try:
        # 加载模型和数据 ✅ 【这里已修改为大样本模型】
        item_cf_data, als_model_data, df_movies = load_trained_model(model_folder="models")
        movie_sim_matrix = item_cf_data['sim']
        user_rated_dict = item_cf_data['ratings']
        print("✅ 模型预加载完成！服务已就绪。")
    except Exception as e:
        print(f"❌ 模型加载失败：{str(e)}")
        print("请确保已运行过 scripts/recommendation_system_1.py 生成了 models_full_parquet 文件夹")

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

# ---------------------- 4. 所有接口（真实模型版） ----------------------
# 基础接口
@app.get("/api/")
def root():
    return {"message": "Project01 后端服务运行正常！模型已加载！"}

# 推荐接口（真实模型版 + 修复报错）
@app.get("/api/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = 20, model_type: str = "itemcf"):
    if user_id <= 0:
        return error(1001, "用户不存在")
    if df_movies is None or user_rated_dict is None:
        return error(5001, "模型未加载，请检查服务启动日志")
    
    try:
        # 检查用户是否存在
        if user_id not in user_rated_dict:
            print(f"⚠️ 用户 {user_id} 无评分记录，返回热门电影")
            # 修复：兼容无Rating列的情况，仅对不存在的用户生效
            if 'Rating' in df_movies.columns:
                hot_movies = df_movies.sort_values(by='Rating', ascending=False).head(top_n)
            else:
                hot_movies = df_movies.head(top_n)
                
            recommend_list = []
            for _, row in hot_movies.iterrows():
                score = float(row['Rating']) if 'Rating' in df_movies.columns else 3.0
                recommend_list.append({
                    "movie_id": int(row['MovieID']),
                    "title": row['Title'],
                    "score": score,
                    "poster": "",
                    "reason": "热门高分电影"
                })
            return success(data=recommend_list)
        
        # 获取用户已经看过的电影
        user_rated_movies = user_rated_dict[user_id]
        user_rated_ids = set(user_rated_movies.keys())
        # 获取所有电影ID
        all_movie_ids = set(movie_sim_matrix.index)
        # 找出用户没看过的电影（候选集）
        unrated_movie_ids = all_movie_ids - user_rated_ids
        
        # ---------------------- 用ItemCF模型推荐 ----------------------
        if model_type == "itemcf":
            # 存储每个候选电影的预测评分
            movie_pred_score = {}
            
            # 遍历所有没看过的电影，计算预测评分
            for movie_id in unrated_movie_ids:
                # 取和当前电影最相似的top_k个电影
                top_k = 10
                similar_movies = movie_sim_matrix[movie_id].sort_values(ascending=False)[1:top_k+1]
                
                weighted_sum = 0.0
                sim_sum = 0.0
                # 计算加权评分
                for sim_movie_id, sim in similar_movies.items():
                    if sim_movie_id in user_rated_movies:
                        weighted_sum += sim * user_rated_movies[sim_movie_id]
                        sim_sum += sim
                
                # 计算预测评分
                if sim_sum > 0:
                    movie_pred_score[movie_id] = weighted_sum / sim_sum
                else:
                    movie_pred_score[movie_id] = np.mean(list(user_rated_movies.values()))
            
            # 按预测评分降序排序，取top_n
            sorted_movies = sorted(movie_pred_score.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # ---------------------- 整理推荐结果 ----------------------
        recommend_list = []
        for movie_id, pred_score in sorted_movies:
            # 从电影信息表里查电影标题
            movie_info = df_movies[df_movies['MovieID'] == movie_id].iloc[0]
            recommend_list.append({
                "movie_id": int(movie_id),
                "title": movie_info['Title'],
                "score": round(float(pred_score), 2),
                "poster": "",
                "reason": f"基于你的观影历史推荐，预测评分{round(float(pred_score), 2)}分"
            })
        
        print(f"✅ 为用户 {user_id} 生成了 {len(recommend_list)} 条推荐")
        return success(data=recommend_list)
        
    except Exception as e:
        print(f"❌ 生成推荐失败：{str(e)}")
        return error(5001, f"生成推荐失败：{str(e)}")

# 刷新推荐接口（复用推荐逻辑）
@app.post("/api/refresh/{user_id}")
def refresh_recommendations(user_id: int, top_n: int = 20, model_type: str = "itemcf"):
    if user_id <= 0:
        return error(1001, "用户不存在")
    # 刷新推荐和获取推荐逻辑一样，直接调用推荐接口的逻辑
    result = get_recommendations(user_id, top_n, model_type)
    if result['code'] == 0:
        return success(data={"status": "refreshed", "recommendations": result['data']})
    else:
        return result

# 电影详情接口（真实数据版）
@app.get("/api/movie/{movie_id}")
def get_movie_detail(movie_id: int):
    if movie_id <= 0:
        return error(1002, "电影不存在")
    if df_movies is None:
        return error(5001, "模型未加载，请检查服务启动日志")
    
    # 从电影信息表里查真实数据
    movie_info = df_movies[df_movies['MovieID'] == movie_id]
    if len(movie_info) == 0:
        return error(1002, "电影不存在")
    
    movie_info = movie_info.iloc[0]
    return success(data={
        "movie_id": int(movie_info['MovieID']),
        "title": movie_info['Title'],
        "genres": movie_info.get('Genres', '未知'),
        "year": int(movie_info.get('Year', 2000)),
        "rating": float(movie_info.get('Rating', 3.0))
    })

# 相似电影接口（真实数据版）
@app.get("/api/movie/{movie_id}/similar")
def get_similar(movie_id: int, top_n: int = 10):
    if movie_id <= 0:
        return error(1002, "电影不存在")
    if df_movies is None or movie_sim_matrix is None:
        return error(5001, "模型未加载，请检查服务启动日志")
    
    # 检查电影是否在相似度矩阵里
    if movie_id not in movie_sim_matrix.index:
        return error(1002, "电影不存在")
    
    # 取相似度最高的top_n个电影
    similar_movies = movie_sim_matrix[movie_id].sort_values(ascending=False)[1:top_n+1]
    
    # 整理结果
    similar_list = []
    for sim_movie_id, sim_score in similar_movies.items():
        movie_info = df_movies[df_movies['MovieID'] == sim_movie_id].iloc[0]
        similar_list.append({
            "movie_id": int(sim_movie_id),
            "title": movie_info['Title'],
            "score": round(float(sim_score), 2),
            "poster": "",
            "reason": f"相似度：{round(float(sim_score)*100, 1)}%"
        })
    
    return success(data=similar_list)

# 用户反馈接口（保持不变，后续可接入数据库）
@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackRequest):
    if feedback.user_id <= 0 or feedback.movie_id <= 0:
        return error(1003, "参数无效")
    return success(data={"status": "received"})

# 统计概览接口（真实数据版）
@app.get("/api/stats/overview")
def get_stats():
    if df_movies is None or user_rated_dict is None:
        return error(5001, "模型未加载，请检查服务启动日志")
    
    # 计算真实的统计数据
    total_users = len(user_rated_dict)
    total_movies = len(df_movies)
    # 修复：兼容无Rating列
    if 'Rating' in df_movies.columns:
        avg_rating = round(float(df_movies['Rating'].mean()), 2)
    else:
        avg_rating = 3.0
    
    # 计算总评分数（估算）
    total_ratings = 0
    for user_ratings in user_rated_dict.values():
        total_ratings += len(user_ratings)
    
    return success(data={
        "total_users": total_users,
        "total_movies": total_movies,
        "total_ratings": total_ratings,
        "avg_rating": avg_rating
    })