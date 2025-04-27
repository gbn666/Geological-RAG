// src/services/auth_service.js
import axios from 'axios';

// 从环境变量或默认值读取后端 URL
const API_BASE = process.env.VUE_APP_API_BASE_URL || 'http://172.20.5.23:5000';

// 创建 Axios 实例，指向后端 auth 路由
const authClient = axios.create({
  baseURL: `${API_BASE}/api/auth`,
  timeout: 5000,
});

// 请求拦截器：自动注入 Authorization 头
authClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器：统一错误处理
authClient.interceptors.response.use(
  response => response,
  error => {
    // 可以根据需要处理 401（未授权）、403（禁止）等
    if (error.response && error.response.status === 401) {
      // TODO: 可触发登出逻辑或跳转登录页
      localStorage.removeItem('access_token');
    }
    return Promise.reject(error);
  }
);

/**
 * 发送验证码到邮箱
 * @param {string} email
 * @returns {Promise}
 */
export function sendVerificationCode(email) {
  return authClient
    .post('/sendCode', { email })
    .then(res => res.data);
}

/**
 * 用户注册
 * @param {string} email
 * @param {string} password
 * @param {string|number} verificationCode
 * @returns {Promise}
 */
export function register(email, password, verificationCode) {
  return authClient
    .post('/register', { email, password, verificationCode })
    .then(res => res.data);
}

/**
 * 用户登录
 * @param {string} email
 * @param {string} password
 * @returns {Promise}
 */
export function login(email, password) {
  return authClient
    .post('/login', { email, password })
    .then(res => {
      const { access_token, expires_in } = res.data;
      // 将 token 和过期时间存储到 localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token_expires_at', Date.now() + expires_in * 1000);
      return res.data;
    });
}

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export function getCurrentUser() {
  return authClient
    .get('/me')
    .then(res => res.data);
}

/**
 * 登出，清理本地存储
 */
export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token_expires_at');
}
