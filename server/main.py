from fastapi import FastAPI
from api import router

app = FastAPI(title="Project01 推荐系统", version="1.0")

app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Project01 后端服务运行正常！"}