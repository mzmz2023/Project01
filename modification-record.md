# 后端（集成工程师）修改记录

> 生成日期：2026-05-05
> 说明：本文档记录对 member C 交付物的所有修改，便于回溯与审查。

---

## 修改清单

### 1. 新增 .gitignore（根目录）

**文件**：`.gitignore`（新建）

**内容**：忽略 `__pycache__/`、`*.pyc`、`data_env/`、`.venv/`、`*.db`、`*.gitkeep` 等无需跟踪的文件。

---

### 2. 新增 .dockerignore

**文件**：`.dockerignore`（新建）

**内容**：排除 `.git/`、`__pycache__/`、`data_env/`、`notebooks/`、`data/`、`models/` 等，减少镜像体积。

---

### 3. 新增 requirements.txt

**文件**：`requirements.txt`（新建）

**内容**：
```
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pandas>=2.0.0
pydantic>=2.0.0
```

---

### 4. 更新 Dockerfile

**文件**：`Dockerfile`

**变更**：
- 将 `COPY . /app` 拆分为两步：先 COPY `requirements.txt` 安装依赖（利用缓存），再 COPY 其余代码
- 改用 `requirements.txt` 安装依赖，而非硬编码 pip install 列表

---

### 5. 修复 docker-compose.yml

**文件**：`docker-compose.yml`

**变更**：
- 修复卷映射路径：`./recommend.db` → `./db/recommend.db`（原路径指向不存在的位置）
- 新增 `frontend` 服务，支持一键启动前后端

---

### 6. 新增 db/schema.sql

**文件**：`db/schema.sql`（新建）

**内容**：定义 6 张表的完整 DDL：
- `users` — 用户表
- `movies` — 电影表（含 title、genres、year）
- `ratings` — 评分记录表（含外键、索引、CHECK 约束）
- `user_features` — 用户特征表
- `movie_features` — 电影特征表
- `rec_cache` — 推荐结果缓存表

---

### 7. 更新 db/init_db.py

**文件**：`db/init_db.py`

**变更**：
- 先执行 `schema.sql` 建表，再导入数据
- `to_sql` 写入模式从 `replace` 改为 `append`（表已由 DDL 创建）
- 增加 `schema.sql` 文件是否存在检查

---

### 8. 新增 server/model_loader.py

**文件**：`server/model_loader.py`（新建）

**内容**：模型加载器占位类 `ModelLoader`，包含：
- `load()` — 加载模型文件
- `predict(user_id, top_n)` — 预测接口
- 全局单例 `model_loader`

---

### 9. 更新 server/main.py

**文件**：`server/main.py`

**变更**：
- 添加 `@app.on_event("startup")` 启动时加载模型
- 添加全局异常处理器 `@app.exception_handler(Exception)`，返回 `{"code": 5001, "message": "服务内部错误", "data": None}`

---

### 10. 更新 api/__init__.py — 绑定响应模型

**文件**：`api/__init__.py`

**变更**：
- 新增 `RecommendListResponse`、`MovieDetailResponse`、`StatsOverviewResponse`、`ApiResponse` 响应模型
- 所有路由添加 `response_model=xxx`，让 Swagger `/docs` 页面自动生成文档
- 推荐接口 mock 数据补全 `poster` 和 `reason` 字段

---

### 11. 更新 api/__init__.py — 统一响应格式

**文件**：`api/__init__.py`

**变更**：
- 成功 `code` 从 `0` 改为 `200`，与 `api-spec.md` 一致
- 新增 `success()` / `error()` 公共响应函数，所有接口统一调用

---

### 12. 更新 api/__init__.py — 补全 6 个接口

**文件**：`api/__init__.py`

**变更**：
- 从 1 个接口扩展到 6 个：
  - `GET /api/recommend/{user_id}?top_n=20` — 推荐列表
  - `GET /api/movie/{movie_id}` — 电影详情
  - `GET /api/movie/{movie_id}/similar?top_n=10` — 相似电影
  - `POST /api/feedback` — 用户反馈
  - `POST /api/refresh/{user_id}` — 刷新推荐
  - `GET /api/stats/overview` — 系统概况

---

### 13. 更新 docs/api-spec.md

**文件**：`docs/api-spec.md`

**变更**：
- 从 1 个接口扩展到 6 个，与代码保持一致
- 新增通用规范章节（base URL、响应格式、错误码表）
- 修复所有表格 Markdown 格式

---

## 文件变更汇总

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `.gitignore` | Git 忽略规则 |
| 新建 | `.dockerignore` | Docker 构建排除 |
| 新建 | `requirements.txt` | Python 依赖清单 |
| 新建 | `db/schema.sql` | 数据库 DDL |
| 新建 | `server/model_loader.py` | 模型加载器占位 |
| 修改 | `Dockerfile` | 依赖安装优化 |
| 修改 | `docker-compose.yml` | 修复卷路径 + 加前端服务 |
| 修改 | `db/init_db.py` | 改用 schema.sql 建表 |
| 修改 | `server/main.py` | 异常处理 + 模型加载 |
| 修改 | `api/__init__.py` | 补齐接口 + 响应模型 + 统一格式 |
| 修改 | `docs/api-spec.md` | 同步 6 个接口文档 |
