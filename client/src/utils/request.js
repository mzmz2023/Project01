import axios from 'axios';
import { message } from 'antd';

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// 响应拦截器：统一处理 code 和错误
request.interceptors.response.use(
  response => {
    const res = response.data;
    if (res.code !== 0) {
      // 根据错误码显示友好提示
      const errorMsg = getErrorMessage(res.code, res.message);
      message.error(errorMsg);
      return Promise.reject(new Error(errorMsg));
    }
    return res.data; // 直接返回 data 字段内容
  },
  error => {
    message.error(error.message || '网络请求失败');
    return Promise.reject(error);
  }
);

function getErrorMessage(code, defaultMsg) {
  switch (code) {
    case 1001: return '用户不存在';
    case 1002: return '电影不存在';
    case 2001: return '参数错误';
    case 5001: return '服务内部错误';
    default: return defaultMsg || `请求失败 (${code})`;
  }
}

export default request;