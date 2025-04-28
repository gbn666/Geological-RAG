// App.js
import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import MainArea from "./components/MainArea";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);

  // 处理文字消息
  const handleSend = (text) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { type: "text", content: text, sender: "user" }]);
    // TODO: 后端回复逻辑
  };

  // 处理图片上传
  const handleImageUpload = (file) => {
    const url = URL.createObjectURL(file);
    setMessages((prev) => [...prev, { type: "image", content: url, sender: "user" }]);
  };

  return (
    <div className="app-container">
      <Sidebar />
      <MainArea
        messages={messages}
        onSend={handleSend}
        onImageUpload={handleImageUpload}
      />
    </div>
  );
}

export default App;