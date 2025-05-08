// src/api/axiosConfig.js
// src/api/axiosConfig.js
// import axios from 'axios';

// const axiosInstance = axios.create({
//   baseURL: process.env.REACT_APP_API_BASE_URL || '/api',
// });

// axiosInstance.interceptors.request.use(config => {
//   const token = localStorage.getItem('access_token');
//   if (token) config.headers.Authorization = `Bearer ${token}`;
//   return config;
// });



// File: src/api/axiosConfig.js
// -------------------------
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "/api";

const http = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  withCredentials: true,
});

http.interceptors.request.use(config => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

http.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("token_expires_at");
      localStorage.removeItem("user_email");
    }
    return Promise.reject(err);
  }
);

export default http;
