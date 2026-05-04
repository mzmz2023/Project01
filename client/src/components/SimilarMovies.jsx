import React, { useEffect, useState } from 'react';
import { List, Spin, Typography } from 'antd';
import { getSimilarMovies } from '../api/movieApi';
import MovieCard from './MovieCard';

const { Title } = Typography;

const SimilarMovies = ({ movieId }) => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSimilar = async () => {
      setLoading(true);
      try {
        const data = await getSimilarMovies(movieId, 10);
        setMovies(data || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    if (movieId) fetchSimilar();
  }, [movieId]);

  if (loading) return <Spin tip="加载相似电影..." />;
  if (movies.length === 0) return null;

  return (
    <div style={{ marginTop: 32 }}>
      <Title level={4}>相似电影推荐</Title>
      <List
        grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4, xl: 5 }}
        dataSource={movies}
        renderItem={movie => (
          <List.Item>
            <MovieCard movie={movie} />
          </List.Item>
        )}
      />
    </div>
  );
};

export default SimilarMovies;