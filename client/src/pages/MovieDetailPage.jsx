import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Descriptions, Spin, Typography, Rate, Image, Empty, Button, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { getMovieDetail } from '../api/movieApi';
import SimilarMovies from '../components/SimilarMovies';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const MovieDetailPage = () => {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const data = await getMovieDetail(movieId);
        setMovie(data);
      } catch (err) {
        console.error(err);
        setMovie(null);
      } finally {
        setLoading(false);
      }
    };
    if (movieId) fetchDetail();
  }, [movieId]);

  if (loading) return <Spin tip="加载电影详情..." style={{ display: 'block', textAlign: 'center', marginTop: 100 }} />;
  if (!movie) return <Empty description="电影不存在" />;

  return (
    <div style={{ padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>返回</Button>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24 }}>
        <div style={{ flex: '0 0 200px' }}>
          {movie.poster ? <Image src={movie.poster} alt={movie.title} width={200} /> : <div style={{ width: 200, height: 280, background: '#f0f2f5', textAlign: 'center', lineHeight: '280px' }}>暂无海报</div>}
        </div>
        <div style={{ flex: 1 }}>
          <Title level={2}>{movie.title}</Title>
          {movie.rating !== undefined && <Rate disabled defaultValue={movie.rating / 2} allowHalf style={{ fontSize: 16 }} />}
          <Paragraph style={{ marginTop: 16 }}>{movie.overview || '暂无简介'}</Paragraph>
          <Descriptions column={2} bordered style={{ marginTop: 16 }}>
            <Descriptions.Item label="上映年份">{movie.year || '未知'}</Descriptions.Item>
            <Descriptions.Item label="类型">{movie.genres?.join(', ') || '未知'}</Descriptions.Item>
            <Descriptions.Item label="时长">{movie.runtime ? `${movie.runtime}分钟` : '未知'}</Descriptions.Item>
            <Descriptions.Item label="评分">{movie.rating || '暂无评分'}</Descriptions.Item>
          </Descriptions>
        </div>
      </div>
      <SimilarMovies movieId={movieId} />
    </div>
  );
};

export default MovieDetailPage;