import React from 'react';
import { Card, Typography, Rate, Button, Space, Tooltip } from 'antd';
import { LikeOutlined, DislikeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Text, Paragraph } = Typography;

const MovieCard = ({ movie, showFeedback = false, onFeedback, feedbackLoading = false }) => {
  const navigate = useNavigate();
  const { movie_id, title, poster, rating, recommendation_reason } = movie;

  const handleClick = () => {
    navigate(`/movie/${movie_id}`);
  };

  const handleLike = (e) => {
    e.stopPropagation();
    onFeedback && onFeedback(movie_id, 'like');
  };

  const handleDislike = (e) => {
    e.stopPropagation();
    onFeedback && onFeedback(movie_id, 'dislike');
  };

  return (
    <Card
      hoverable
      cover={poster ? <img alt={title} src={poster} style={{ height: 280, objectFit: 'cover' }} /> : <div style={{ height: 280, background: '#f0f2f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>暂无海报</div>}
      onClick={handleClick}
      style={{ width: 200, margin: '8px' }}
      bodyStyle={{ padding: '12px' }}
    >
      <Tooltip title={title}>
        <Text strong ellipsis style={{ display: 'block', fontSize: '14px' }}>{title}</Text>
      </Tooltip>
      {rating !== undefined && <Rate disabled defaultValue={rating / 2} allowHalf style={{ fontSize: '12px' }} />}
      {recommendation_reason && <Paragraph ellipsis={{ rows: 2 }} style={{ fontSize: '12px', color: '#888', marginTop: 4 }}>推荐理由：{recommendation_reason}</Paragraph>}
      {showFeedback && (
        <Space style={{ marginTop: 8 }}>
          <Button size="small" icon={<LikeOutlined />} onClick={handleLike} loading={feedbackLoading} />
          <Button size="small" icon={<DislikeOutlined />} onClick={handleDislike} loading={feedbackLoading} />
        </Space>
      )}
    </Card>
  );
};

export default MovieCard;