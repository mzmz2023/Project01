# server — 后端服务

## 职责

FastAPI 应用入口，服务启动配置，全局异常处理，模型加载。

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | FastAPI 应用实例，注册路由、异常处理器、启动时加载模型 |
| `model_loader.py` | 模型加载器，封装 B 同学训练的推荐模型，提供 `predict()` 接口 |

## 启动方式

```bash
# 直接运行
uvicorn server.main:app --host 0.0.0.0 --port 8000

# 或通过 docker-compose
docker-compose up
```

## 接口文档

启动后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

## 依赖

- FastAPI
- uvicorn
