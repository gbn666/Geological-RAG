// -------------------------
// File: src/api/auth.js
// -------------------------
import http from "./axiosConfig";

export function sendVerificationCode(email) {
  return http.post("/auth/sendCode", { email });
}

export function register(email, password, verificationCode) {
  return http.post("/auth/register", { email, password, verificationCode });
}

export function login(email, password) {
  return http.post("/auth/login", { email, password }).then(res => {
    const { access_token, expires_in } = res.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("token_expires_at", Date.now() + expires_in * 1000);
    localStorage.setItem("user_email", email);
    return res.data;
  });
}

export function getCurrentUser() {
  return http.get("/auth/me").then(res => res.data);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_expires_at");
  localStorage.removeItem("user_email");
}

export function changePassword(currentPassword, newPassword) {
  return http.post("/auth/changePassword", { currentPassword, newPassword });
}

