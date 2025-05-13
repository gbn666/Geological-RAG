// // src/api/session.js0511
// import http from "./axiosConfig";

// // 创建一个新的对话 Session
// export function createSession() {
//   return http
//     .post("/session/new")
//     .then(res => res.data.session_id);
// }

// // 列出当前用户所有会话
// export function listSessions() {
//   return http
//     .get("/session/list")
//     .then(res => res.data.sessions);
// }



// src/api/session.js
// File: src/api/session.js
import http from "./axiosConfig";

// 创建新会话
export function createSession() {
  return http
    .post("/session/new")
    .then(res => res.data.session_id);
}

// 获取当前用户的所有会话列表
export function listSessions() {
  return http
    .get("/session/list")
    .then(res => res.data.sessions);
}

