// File: src/App.js0511
import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import MainArea from "./components/MainArea";
import { createSession, sendMessage } from "./api/chat";
import { uploadImage } from "./api/upload";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState("");

  // onSend 会返回一个 Promise，ChatInput 可以 await 它
  const handleSend = async (text, file) => {
    if (!text.trim() && !file) {
      throw new Error("请输入文字或选择图片");
    }

    // —— 按需创建会话 —— 
    let sid = sessionId;
    if (!sid) {
      sid = await createSession();
      setSessionId(sid);
    }

    // —— Optimistic UI 渲染用户消息 —— 
    const userMsgs = [];
    const trimmed = text.trim();
    if (trimmed) {
      userMsgs.push({ type: "text", content: trimmed, sender: "user" });
    }
    let previewUrl;
    if (file) {
      previewUrl = URL.createObjectURL(file);
      userMsgs.push({ type: "image", content: previewUrl, sender: "user" });
    }
    setMessages(prev => [...prev, ...userMsgs]);

    // —— 上传图片（可选） —— 
    let imageUrl;
    if (file) {
      try {
        const resp = await uploadImage(file);
        imageUrl = resp.data.image_url;
      } catch {
        // 上传失败就用本地预览也能继续
        imageUrl = previewUrl;
      }
    }

    // —— 调用后端接口 —— 
    const res = await sendMessage(sid, {
      question: trimmed || undefined,
      imageUrl,
    });

    // —— 渲染机器人回复 —— 
    setMessages(prev => [
      ...prev,
      { type: "text", content: res.answer, sender: "bot" },
    ]);
    return res;
  };

  return (
    <div className="app-container">
      <Sidebar />
      <MainArea
        messages={messages}
        onSend={handleSend}
        hasMessage={messages.length > 0}
      />
    </div>
  );
}

export default App;




