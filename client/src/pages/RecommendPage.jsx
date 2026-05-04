import React, { useState, useEffect } from 'react';
import { Row, Col, Typography, Button, InputNumber, Spin, Empty, message, Alert } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { getRecommendations, refreshRecommendations, submitFeedback } from '../api/movieApi';
import MovieCard from '../components/MovieCard';

const { Title, Text } = Typography;

const RecommendPage = () => {
  const [userId, setUserId] = useState(1); // 示例用户ID，可改成输入框或登录逻辑
  const [topN, setTopN] = useState(20);
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [refreshLoading, setRefreshLoading] = useState(false);

  const fetchRecommendations = async (refresh = false) => {
    setLoading(true);
    try {
      let data;
      if (refresh) {
        await refreshRecommendations(userId);
        message.success('推荐已刷新');
      }
      data = await getRecommendations(userId, topN);
      setMovies(data || []);
    } catch (err) {
      console.error(err);
      setMovies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [userId, topN]);

  const handleFeedback = async (movieId, type) => {
    setFeedbackLoading(true);
    try {
      await submitFeedback(userId, movieId, type);
      message.success(`已${type === 'like' ? '喜欢' : '不感兴趣'}电影`);
      // 可选：重新获取推荐或更新本地状态
      fetchRecommendations();
    } catch (err) {
      message.error('反馈提交失败');
    } finally {
      setFeedbackLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshLoading(true);
    fetchRecommendations(true).finally(() => setRefreshLoading(false));
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>为你推荐</Title>
        <div>
          <Text style={{ marginRight: 8 }}>用户ID：</Text>
          <InputNumber min={1} value={userId} onChange={setUserId} style={{ width: 100, marginRight: 16 }} />
          <Text style={{ marginRight: 8 }}>推荐数量：</Text>
          <InputNumber min={1} max={100} value={topN} onChange={setTopN} style={{ width: 80, marginRight: 16 }} />
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={refreshLoading}>刷新推荐</Button>
        </div>
      </div>
      {loading ? (
        <Spin size="large" tip="加载推荐中..." style={{ display: 'block', textAlign: 'center', marginTop: 100 }} />
      ) : movies.length === 0 ? (
        <Empty description="暂无推荐，请尝试刷新或更换用户" />
      ) : (
        <Row gutter={[16, 16]}>
          {movies.map(movie => (
            <Col key={movie.movie_id} xs={12} sm={8} md={6} lg={4} xl={4}>
              <MovieCard movie={movie} showFeedback onFeedback={handleFeedback} feedbackLoading={feedbackLoading} />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default RecommendPage;