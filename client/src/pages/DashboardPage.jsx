import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Spin, Typography, List, Progress, Avatar } from 'antd';
import { getStatsOverview } from '../api/movieApi';
import { UserOutlined, StarOutlined, FireOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const data = await getStatsOverview();
        setStats(data);
      } catch (err) {
        console.error(err);
        setStats(null);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <Spin tip="加载仪表盘数据..." style={{ display: 'block', textAlign: 'center', marginTop: 100 }} />;
  if (!stats) return <div>暂无统计数据，请确保后端提供了 /api/stats/overview 接口</div>;

  // 假设后端返回的数据结构
  const { hot_movies, rating_distribution, user_profile } = stats;

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>数据仪表盘</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title={<><FireOutlined /> 热门电影Top10</>} bordered>
            <List
              dataSource={hot_movies || []}
              renderItem={(item, idx) => (
                <List.Item>
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                    <span>{idx+1}. {item.title}</span>
                    <Text type="secondary">{item.recommend_count || item.rating_count}次推荐</Text>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title={<><StarOutlined /> 评分分布</>} bordered>
            {rating_distribution ? (
              Object.entries(rating_distribution).map(([score, count]) => (
                <div key={score} style={{ marginBottom: 12 }}>
                  <Text>{score} 星</Text>
                  <Progress percent={(count / Object.values(rating_distribution).reduce((a,b)=>a+b,0)) * 100} size="small" />
                </div>
              ))
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title={<><UserOutlined /> 用户画像摘要</>} bordered>
            {user_profile ? (
              <>
                <p>总用户数：{user_profile.total_users}</p>
                <p>平均年龄：{user_profile.avg_age}</p>
                <p>性别比例：男 {user_profile.male_ratio}% / 女 {user_profile.female_ratio}%</p>
                <p>最活跃职业：{user_profile.top_occupation}</p>
              </>
            ) : (
              <Text type="secondary">暂无用户画像数据</Text>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;