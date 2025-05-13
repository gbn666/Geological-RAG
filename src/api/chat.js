// // // File: src/api/chat0511.js
// // import http from "./axiosConfig";

// // // 创建一个新的对话 Session，返回 session_id 给前端
// // export function createSession() {
// //   return http
// //     .post("/session/new")
// //     .then(res => res.data.session_id);
// // }

// // // 发送文本或图片消息
// // // 接收 question（可选）和 imageUrl（可选）两个参数
// // export function sendMessage(sessionId, { question, imageUrl }) {
// //   // 只将存在的字段加到 payload
// //   const payload = {};
// //   if (question != null && question !== "") {
// //     payload.question = question;
// //   }
// //   if (imageUrl) {
// //     payload.image_url = imageUrl;
// //   }

// //   return http
// //     .post(`/session/${sessionId}/chat`, payload, { timeout: 120000 })
// //     .then(res => res.data);
// // }





// // File: src/api/chat.js

// import http from "./axiosConfig";

// /**
//  * 创建一个新的对话 Session
//  * @returns {Promise<string>} 返回新创建的 session_id
//  */
// export function createSession() {
//   return http
//     .post("/session/new")
//     .then(res => res.data.session_id);
// }

// /**
//  * 获取当前用户的所有会话列表
//  * @returns {Promise<Array<{session_id: string, created_at: string}>>}
//  */
// export function listSessions() {
//   return http
//     .get("/session/list")
//     .then(res => res.data.sessions);
// }

// /**
//  * 获取指定会话的完整历史消息
//  * @param {string} sessionId 会话 ID
//  * @returns {Promise<Array<{sender: string, type: string, content: string}>>}
//  */
// export function getSessionHistory(sessionId) {
//   return http
//     .get(`/session/${sessionId}/chat`)
//     .then(res => res.data);
// }

// /**
//  * 发送文本或图片消息到指定会话
//  * @param {string} sessionId 会话 ID
//  * @param {{question?: string, imageUrl?: string}} options
//  *        question - 文本消息（可选）
//  *        imageUrl - 图片 URL（可选）
//  * @returns {Promise<{answer: string}>} 后端返回的数据（例如机器人的回答）
//  */
// export function sendMessage(sessionId, { question, imageUrl }) {
//   // 构造请求 payload，只包含非空字段
//   const payload = {};
//   if (question != null && question !== "") {
//     payload.question = question;
//   }
//   if (imageUrl) {
//     payload.image_url = imageUrl;
//   }

//   return http
//     .post(`/session/${sessionId}/chat`, payload, { timeout: 120000 })
//     .then(res => res.data);
// }




// // File: src/api/chat.js
// import http from "./axiosConfig";

// // 创建一个新的对话 Session，返回 session_id
// export function createSession() {
//   return http
//     .post("/session/new")
//     .then(res => res.data.session_id);
// }

// // 获取当前用户所有会话列表
// export function listSessions() {
//   return http
//     .get("/session/list")
//     .then(res => res.data.sessions);
// }

// // 获取指定会话的历史消息
// export function getSessionHistory(sessionId) {
//   return http
//     .get(`/session/${sessionId}/chat`)
//     .then(res => res.data);
// }

// // 发送文本或图片消息
// export function sendMessage(sessionId, { question, imageUrl }) {
//   const payload = {};
//   if (question != null && question !== "") {
//     payload.question = question;
//   }
//   if (imageUrl) {
//     payload.image_url = imageUrl;
//   }
//   return http
//     .post(`/session/${sessionId}/chat`, payload, { timeout: 120000 })
//     .then(res => res.data);
// }

// File: src/api/chat.js
// import http from "./axiosConfig";

// /**
//  * 创建一个新的对话 Session，返回 session_id
//  */
// export function createSession() {
//   return http
//     .post("/session/new")
//     .then(res => res.data.session_id);
// }

// /**
//  * 获取当前用户所有会话列表
//  */
// export function listSessions() {
//   return http
//     .get("/session/list")
//     .then(res => res.data.sessions);
// }

// /**
//  * 获取指定会话的历史消息
//  * （调用后端新增的 /api/session/messages?session_id=... 接口）
//  */
// export function getSessionHistory(sessionId) {
//   return http
//     .get("/session/messages", {
//       params: { session_id: sessionId }
//     })
//     .then(res => res.data.messages);
// }

// /**
//  * 发送文本或图片消息
//  * （调用后端的 /api/chat/send 接口，将 session_id、question、imageUrl 一起提交）
//  */
// export function sendMessage(sessionId, { question, imageUrl }) {
//   const payload = { session_id: sessionId };
//   if (question != null && question !== "") {
//     payload.question = question;
//   }
//   if (imageUrl) {
//     payload.imageUrl = imageUrl;
//   }
//   return http
//     .post("/chat/send", payload, { timeout: 120000 })
//     .then(res => res.data);
// }


// File: src/api/chat.js
import http from "./axiosConfig";

/**
 * 创建一个新的对话 Session，返回 session_id
 */
export function createSession() {
  return http
    .post("/session/new")
    .then(res => res.data.session_id);
}

/**
 * 列出所有会话
 */
export function listSessions() {
  return http
    .get("/session/list")
    .then(res => res.data.sessions);
}

/**
 * 获取指定会话的历史消息
 */
export function getSessionHistory(sessionId) {
  return http
    .get("/session/messages", { params: { session_id: sessionId } })
    .then(res => res.data.messages);
}

/**
 * 发送文本或图片消息（使用 JSON 请求，而非 multipart）
 */
export function sendMessage(sessionId, { question, imageUrl }) {
  const payload = {
    question: question || null,
    imageUrl: imageUrl || null,
  };

   return http.post(`/session/${sessionId}/chat`, payload, {
    headers: { "Content-Type": "application/json" },
    timeout: 180000  // 180秒
  }).then(res => res.data);
}
