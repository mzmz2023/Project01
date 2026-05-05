import sys
import os
# 关键：把项目根目录加入Python路径，确保能找到api模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from api import router

app = FastAPI(title="Project01 推荐系统API")

# 根路径测试接口
@app.get("/")
def read_root():
    return {"message": "Project01 后端服务运行正常！"}

# 注册所有API接口，加上/api前缀
app.include_router(router, prefix="/api")

# 启动入口（必须保留）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",  # 这里必须改成 server.main:app
        host="127.0.0.1",
        port=8000,
        reload=True
    )