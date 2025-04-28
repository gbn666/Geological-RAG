//api.js
import axios from "axios";

// 后端地址，可通过 .env 中 REACT_APP_API_BASE_URL 覆盖
const API_BASE = process.env.REACT_APP_API_BASE_URL
  || "http://172.20.5.23:5000/api/auth";

const authClient = axios.create({
  baseURL: API_BASE,
  timeout: 5000,
});

authClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  err => Promise.reject(err)
);

authClient.interceptors.response.use(
  res => res,
  err => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("token_expires_at");
      localStorage.removeItem("user_email");
    }
    return Promise.reject(err);
  }
);

export function sendVerificationCode(email) {
  return authClient.post("/sendCode", { email });
}

export function register(email, password, verificationCode) {
  return authClient.post("/register", { email, password, verificationCode });
}

export function login(email, password) {
  return authClient.post("/login", { email, password }).then(res => {
    const { access_token, expires_in } = res.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("token_expires_at", Date.now() + expires_in * 1000);
    return res.data;
  });
}

export function getCurrentUser() {
  return authClient.get("/me").then(res => res.data);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_expires_at");
  localStorage.removeItem("user_email");
}

// 新增：修改密码接口
export function changePassword(currentPassword, newPassword) {
  return authClient.post("/changePassword", { currentPassword, newPassword });
}
