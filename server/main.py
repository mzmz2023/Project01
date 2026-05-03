from fastapi import FastAPI
from api import router # 导入我们的接口文件

app = FastAPI(title="Project01 推荐系统API")

# 根路径测试接口
@app.get("/")
def read_root():
    return {"message": "Project01 后端服务运行正常！"}

# 注册所有API接口，统一加上/api前缀
app.include_router(router, prefix="/api")