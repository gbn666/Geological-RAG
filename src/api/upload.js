// File: src/api/upload.js0511
import http from "./axiosConfig";

export function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);
  return http.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}
