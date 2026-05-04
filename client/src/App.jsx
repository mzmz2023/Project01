import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { HomeOutlined, DesktopOutlined, DashboardOutlined } from '@ant-design/icons';
import RecommendPage from './pages/RecommendPage';
import MovieDetailPage from './pages/MovieDetailPage';
import DashboardPage from './pages/DashboardPage';

const { Header, Content, Footer } = Layout;

const App = () => {
  const location = useLocation();

  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: <Link to="/">个人推荐</Link> },
    { key: '/dashboard', icon: <DashboardOutlined />, label: <Link to="/dashboard">数据仪表盘</Link> },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold', marginRight: 40 }}>🎬 电影推荐系统</div>
        <Menu theme="dark" mode="horizontal" selectedKeys={[location.pathname]} items={menuItems} style={{ flex: 1 }} />
      </Header>
      <Content style={{ padding: '0 24px', marginTop: 24 }}>
        <div style={{ background: '#fff', minHeight: 380, borderRadius: 8 }}>
          <Routes>
            <Route path="/" element={<RecommendPage />} />
            <Route path="/movie/:movieId" element={<MovieDetailPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>电影推荐系统 ©2026 前端工程师D 实现</Footer>
    </Layout>
  );
};

export default App;