from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api import router
from server.model_loader import model_loader

app = FastAPI(title="Project01 推荐系统API")

# 启动时加载模型
@app.on_event("startup")
def startup():
    model_loader.load()

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 5001, "message": "服务内部错误", "data": None},
    )

# 根路径测试接口
@app.get("/")
def read_root():
    return {"message": "Project01 后端服务运行正常！"}

# 注册所有API接口，统一加上/api前缀
app.include_router(router, prefix="/api")