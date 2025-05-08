// src/api/chat.js
// src/api/chat.js
// import axios from "axios";

// const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://172.20.97.54:5000/api";

// /**
//  * 创建新会话
//  * @returns {Promise<{ session_id: string }>}
//  */
// export function createSession() {
//   const token = localStorage.getItem("access_token");
//   return axios.post(`${API_BASE}/session/new`, {}, {
//     headers: {
//       ...(token ? { Authorization: `Bearer ${token}` } : {}),
//     },
//   });
// }

// /**
//  * 发送消息（图文）
//  * @param {string} sessionId
//  * @param {{ text?: string, imageUrl?: string }} payload
//  * @returns {Promise<{ answer: string, kg_candidates: Array }>}
//  */
// export function sendMessage(sessionId, payload) {
//   const token = localStorage.getItem("access_token");
//   return axios.post(`${API_BASE}/session/${sessionId}/chat`, {
//     question: payload.text || "",
//     image_path: payload.imageUrl || null,
//   }, {
//     headers: {
//       "Content-Type": "application/json",
//       ...(token ? { Authorization: `Bearer ${token}` } : {}),
//     },
//   });
// }


// src/api/chat.js
// src/api/chat.js
// import axios from "./axiosConfig";

// /** 新建会话 → POST /api/chat/new */
// export const newSession = () => {
//   return axios.post("/session/new");//！注意是后端路径
// };

// /**
//  * 发送消息 → POST /api/chat/{sessionId}/chat
//  * @param {string} sessionId
//  * @param {{ text?: string, imageUrl?: string }} opts
//  */
// export const sendMessage = (sessionId, { text, imageUrl }) => {
//   const payload = {};
//   if (text)     payload.question   = text;
//   if (imageUrl) payload.image_path = imageUrl;
//   return axios.post(`/session/${sessionId}/chat`, payload);//！注意是后端路径
// };


// File: src/api/chat.js
// -------------------------
// import http from "./axiosConfig";

// export function createSession() {
//   return http.post("/session/new").then(res => res.data.session_id);
// }

// export function sendMessage(sessionId, { question, image_path }) {
//   const payload = {};
//   if (question)    payload.question    = question;
//   if (image_path)  payload.image_path  = image_path;
//   return http.post(`/session/${sessionId}/chat`, payload).then(res => res.data);
// }
import http from "./axiosConfig";

// 创建一个新的对话 Session，返回 session_id 给前端
export function createSession() {
  // 注意：后端 Blueprint 前缀是 /api/session
  return http
    .post("/session/new")
    .then(res => res.data.session_id);
}

// 发送文本或图片消息
// 参数：
//   sessionId — 会话 ID  
//   options — 包含可选字段 question（文本）和 imageUrl（图片路径）
export function sendMessage(sessionId, { question, imageUrl }) {
  const payload = {};
  if (question) {
    payload.question = question;
  }
  if (imageUrl) {
    // 后端接收字段名是 image_url
    payload.image_url = imageUrl;
  }

  return http.post(
       `/session/${sessionId}/chat`,
        payload,
       { timeout: 60000 }      // 单独给聊天接口 60s 超时
      )
     .then(res => res.data);
}
 



