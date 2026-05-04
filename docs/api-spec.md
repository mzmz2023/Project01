# API 接口规范

> 本项目 API 接口规范文档，由 member C 负责维护。
> 前后端及算法模块均按此规范开发，如需调整需团队协商。

---

## 通用规范

### 基础地址

```
http://<host>:8000/api
```

### 通用响应格式

所有接口统一返回以下 JSON 结构：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200 为成功 |
| message | string | 状态描述 |
| data | object/array | 响应数据，失败时为 null |

### 错误码

| 错误码 | 含义 |
|--------|------|
| 200 | 成功 |
| 1001 | 用户不存在 |
| 1002 | 电影不存在 |
| 2001 | 参数错误 |
| 5001 | 服务内部错误 |

错误响应示例：

```json
{
  "code": 1001,
  "message": "用户不存在",
  "data": null
}
```

---

## 1. 获取推荐列表

获取指定用户的个性化电影推荐。

### 接口地址

`GET /api/recommend/{user_id}`

### 请求参数

| 参数名 | 类型 | 位置 | 是否必须 | 说明 |
|--------|------|------|----------|------|
| user_id | int | path | 是 | 用户唯一 ID |
| top_n | int | query | 否 | 返回数量，默认 20 |

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "movie_id": 1,
      "title": "示例高分电影1",
      "score": 4.8
    },
    {
      "movie_id": 2,
      "title": "示例高分电影2",
      "score": 4.5
    }
  ]
}
```

### data 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| movie_id | int | 电影 ID |
| title | string | 电影名称 |
| score | float | 推荐得分 |

---

## 2. 获取电影详情

获取单部电影的元信息。

### 接口地址

`GET /api/movie/{movie_id}`

### 请求参数

| 参数名 | 类型 | 位置 | 是否必须 | 说明 |
|--------|------|------|----------|------|
| movie_id | int | path | 是 | 电影唯一 ID |

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "movie_id": 1,
    "title": "示例电影",
    "genres": "Action|Drama",
    "year": 2020,
    "rating": 4.5
  }
}
```

### data 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| movie_id | int | 电影 ID |
| title | string | 电影名称 |
| genres | string | 类型（竖线分隔） |
| year | int | 上映年份 |
| rating | float | 平均评分 |

---

## 3. 获取相似电影

根据指定电影返回相似电影列表。

### 接口地址

`GET /api/movie/{movie_id}/similar`

### 请求参数

| 参数名 | 类型 | 位置 | 是否必须 | 说明 |
|--------|------|------|----------|------|
| movie_id | int | path | 是 | 电影唯一 ID |
| top_n | int | query | 否 | 返回数量，默认 10 |

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "movie_id": 101,
      "title": "相似电影1",
      "score": 4.2
    },
    {
      "movie_id": 102,
      "title": "相似电影2",
      "score": 4.0
    }
  ]
}
```

### data 字段说明

同"获取推荐列表"的 data 字段格式。

---

## 4. 提交用户反馈

用户对推荐结果进行反馈（喜欢 / 不感兴趣）。

### 接口地址

`POST /api/feedback`

### 请求体格式

```json
{
  "user_id": 1,
  "movie_id": 10,
  "action": "like"
}
```

### 请求参数字段

| 参数名 | 类型 | 是否必须 | 说明 |
|--------|------|----------|------|
| user_id | int | 是 | 用户 ID |
| movie_id | int | 是 | 电影 ID |
| action | string | 是 | 反馈类型：`like`（喜欢）或 `dislike`（不感兴趣） |

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "received"
  }
}
```

---

## 5. 刷新推荐结果

强制刷新指定用户的推荐缓存，生成新的推荐结果。

### 接口地址

`POST /api/refresh/{user_id}`

### 请求参数

| 参数名 | 类型 | 位置 | 是否必须 | 说明 |
|--------|------|------|----------|------|
| user_id | int | path | 是 | 用户唯一 ID |

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message": "推荐结果已刷新"
  }
}
```

---

## 6. 系统概况

获取系统整体统计数据（供仪表盘使用）。

### 接口地址

`GET /api/stats/overview`

### 请求参数

无

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 1000,
    "total_movies": 5000,
    "total_ratings": 100000,
    "avg_rating": 3.8
  }
}
```

### data 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| total_users | int | 用户总数 |
| total_movies | int | 电影总数 |
| total_ratings | int | 评分总数 |
| avg_rating | float | 平均评分 |

---

## 7. 算法对接格式

### 后端传给算法的格式

```json
{
  "user_id": 1
}
```

### 算法返回给后端的格式

```json
[
  {
    "movie_id": 101,
    "title": "电影名称",
    "score": 4.8
  },
  {
    "movie_id": 102,
    "title": "电影名称2",
    "score": 4.5
  }
]
```
