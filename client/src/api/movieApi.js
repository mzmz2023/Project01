import request from '../utils/request';

// 获取用户个性化推荐
export const getRecommendations = (userId, topN = 20) => {
  return request.get(`/recommend/${userId}`, { params: { top_n: topN } });
};

// 获取电影详情
export const getMovieDetail = (movieId) => {
  return request.get(`/movie/${movieId}`);
};

// 获取相似电影
export const getSimilarMovies = (movieId, topN = 10) => {
  return request.get(`/movie/${movieId}/similar`, { params: { top_n: topN } });
};

// 提交反馈（喜欢/不喜欢）
export const submitFeedback = (userId, movieId, feedbackType) => {
  return request.post('/feedback', { user_id: userId, movie_id: movieId, feedback: feedbackType });
};

// 刷新用户推荐
export const refreshRecommendations = (userId) => {
  return request.post(`/refresh/${userId}`);
};

// 获取仪表盘概况数据
export const getStatsOverview = () => {
  return request.get('/stats/overview');
};