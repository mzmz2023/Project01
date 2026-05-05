# client — 前端可视化

## 职责

电影推荐系统的 Web 前端界面，负责推荐结果展示、电影详情、数据仪表盘。

## 技术栈

- **框架**：React 18
- **构建工具**：Vite 4
- **UI 库**：Ant Design 5
- **路由**：React Router 6
- **HTTP 请求**：Axios

## 目录结构

```
client/
├── .env                        # 环境变量（后端 API 地址）
├── index.html                  # HTML 入口
├── package.json                # 依赖与脚本
├── vite.config.js              # Vite 配置（含 /api 代理到后端）
└── src/
    ├── main.jsx                # React 入口，挂载路由与 Ant Design 配置
    ├── App.jsx                 # 根组件：布局、导航菜单、路由注册
    ├── api/
    │   └── movieApi.js         # 6 个 API 接口的封装函数
    ├── utils/
    │   └── request.js          # Axios 实例 + 响应拦截器 + 错误码处理
    ├── pages/
    │   ├── RecommendPage.jsx   # 个人推荐页：推荐列表 + 反馈 + 刷新
    │   ├── MovieDatailPage.jsx # 电影详情页：元信息 + 相似电影
    │   └── DashboardPage.jsx   # 数据仪表盘：热门电影 + 评分分布 + 用户画像
    └── components/
        ├── MovieCard.jsx       # 电影卡片组件（海报、评分、推荐理由、反馈按钮）
        ├── FeedbackButtons.jsx # 反馈按钮组件（占位，当前未使用）
        └── SimilarMovies.jsx   # 相似电影列表组件
```

## 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | RecommendPage | 用户推荐列表，支持切换用户 ID、调整数量、反馈、刷新 |
| `/movie/:movieId` | MovieDetailPage | 电影详情、评分、相似推荐 |
| `/dashboard` | DashboardPage | 系统概况仪表盘 |

## 快速启动

```bash
cd client
npm install
npm run dev          # 开发模式，默认端口 3000
npm run build        # 生产构建
```

## 后端对接

前端通过 Vite proxy 将 `/api` 请求转发到后端：

```
开发环境：Vite proxy → http://localhost:8000（vite.config.js 配置）
生产环境：.env 中 VITE_API_BASE_URL 指定后端地址
```

所有 API 调用通过 `src/utils/request.js` 中的 Axios 实例发出，响应拦截器统一处理错误码并弹出提示。

## 注意事项

1. **响应 code 校验**：`src/utils/request.js` 第 14 行拦截器判断 `res.code !== 0` 时报错。当前后端返回的 code 为 `200`，需确认并统一（修改拦截器逻辑或调整后端 code）。
2. **DashboardPage 数据字段**：页面期望的 `hot_movies`、`rating_distribution`、`user_profile` 字段与后端 `/api/stats/overview` 返回的字段（`total_users`、`total_movies` 等）不一致，联调时需对齐。
3. **FeedbackButtons 组件**：当前为空文件，反馈功能已内联在 `MovieCard` 和 `RecommendPage` 中，后续可清理。
4. **文件名拼写**：`MovieDatailPage.jsx` 中 `Datail` 应为 `Detail`，如需修正请同步更新 `App.jsx` 中的 import。
