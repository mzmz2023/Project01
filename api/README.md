# api — API 路由

## 职责

定义后端 RESTful API 路由、请求/响应数据模型。

## 文件说明

| 文件 | 说明 |
|------|------|
| `__init__.py` | 所有 6 个接口的实现，含路由装饰器、Pydantic 模型、公共响应工具函数 |

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recommend/{user_id}?top_n=20` | 获取用户个性化推荐 |
| GET | `/api/movie/{movie_id}` | 获取电影详情 |
| GET | `/api/movie/{movie_id}/similar?top_n=10` | 获取相似电影 |
| POST | `/api/feedback` | 提交用户反馈（like/dislike） |
| POST | `/api/refresh/{user_id}` | 刷新用户推荐结果 |
| GET | `/api/stats/overview` | 系统概况仪表盘数据 |

## 依赖

- FastAPI `APIRouter`
- Pydantic `BaseModel`

## 对接说明

- 所有接口统一返回 `{"code": 200, "message": "success", "data": ...}` 格式
- 推荐接口当前为 mock 数据，待 B 同学模型就绪后调用 `model_loader.predict()` 替换
- 电影详情和概况接口待接入数据库后替换为真实查询
