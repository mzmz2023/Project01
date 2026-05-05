import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from api import router
from server.model_loader import model_loader

app = FastAPI(title="Project01 推荐系统API")

# 关键：服务启动时加载模型
@app.on_event("startup")
def startup_event():
    model_loader.load()

# 根路径测试接口
@app.get("/")
def read_root():
    return {"message": "Project01 后端服务运行正常！"}

# 注册所有API接口，加上/api前缀
app.include_router(router, prefix="/api")

# 启动入口（必须保留）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)