# API 接口规范

> 本项目 API 接口规范文档，由 C 负责维护。

---

## 1. 推荐接口（核心接口）
### 接口地址
`POST /api/recommend`

### 功能说明
根据用户ID，返回个性化电影推荐列表。

### 请求方式
`POST`

---

## 2. 请求格式（前端 → 后端）
### 请求体示例（JSON）
```json
{
  "user_id": 1
}
参数说明
表格
参数名	  类型	   是否必须	        说明
user_id	  int	     是	       用户唯一 ID
3. 算法对接格式（后端 ↔ D）
后端传给算法的格式

{
  "user_id": 1
}


算法返回给后端的格式


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

4. 响应格式（后端 → 前端）

{
  "code": 200,
  "message": "success",
  "data": [
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
}

响应字段说明

字段名	      类型	           说明
code	      int	     状态码，200 = 成功
message	     string	        状态描述
data	     array	        推荐电影列表

列表项字段说明

字段名	      类型	           说明
movie_id	  int	         电影 ID
title	     string	         电影名称
score	     float	         推荐得分

5. 说明
本接口格式为团队统一约定，前后端及算法模块均按此规范开发。
如需新增字段或调整格式，需团队协商后更新此文档。