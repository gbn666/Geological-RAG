
// src/api/upload.js
// import axios from "axios";

// // 后端地址，前后端分离：
// const API_BASE = process.env.REACT_APP_API_BASE_URL
//   || "http://172.20.97.54:5000/api";

// /**
//  * 上传图片
//  * @param {File} file - 仅限 jpg/jpeg/png
//  * @returns {Promise} 成功时 res.data.image_url 会是 "/uploads/xxx.jpg"
//  */
// export function uploadImage(file) {
//   const formData = new FormData();
//   formData.append("file", file);

//   const token = localStorage.getItem("access_token");
//   return axios.post(
//     `${API_BASE.replace(/\/$/, "")}/upload`,
//     formData,
//     {
//       headers: {
//         "Content-Type": "multipart/form-data",
//         ...(token ? { Authorization: `Bearer ${token}` } : {}),
//       },
//     }
//   );
// }


// File: src/api/upload.js
// -------------------------
// import http from "./axiosConfig";

// export function uploadImage(file) {
//   const formData = new FormData();
//   formData.append("file", file);
//   return http.post("/upload", formData, {
//     headers: { "Content-Type": "multipart/form-data" }
//   });
// }


// File: src/api/upload.js
import http from "./axiosConfig";

export function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);
  return http.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}
