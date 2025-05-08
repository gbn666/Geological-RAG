// App.js
// import React, { useState } from "react";
// import Sidebar from "./components/Sidebar";
// import MainArea from "./components/MainArea";
// import "./App.css";

// function App() {
//   const [messages, setMessages] = useState([]);

//   // 处理文字消息
//   const handleSend = (text) => {
//     if (!text.trim()) return;
//     setMessages((prev) => [...prev, { type: "text", content: text, sender: "user" }]);
//     // TODO: 后端回复逻辑
//   };

//   // 处理图片上传
//   const handleImageUpload = (file) => {
//     const url = URL.createObjectURL(file);
//     setMessages((prev) => [...prev, { type: "image", content: url, sender: "user" }]);
//   };

//   return (
//     <div className="app-container">
//       <Sidebar />
//       <MainArea
//         messages={messages}
//         onSend={handleSend}
//         onImageUpload={handleImageUpload}
//       />
//     </div>
//   );
// }

// export default App;

// src/App.js
// src/App.js
// src/App.js
// import React, { useState, useEffect } from "react";
// import Sidebar from "./components/Sidebar";
// import MainArea from "./components/MainArea";
// import { newSession, sendMessage } from "./api/chat";
// import { uploadImage } from "./api/upload";
// import "./App.css";

// function App() {
//   const [messages, setMessages]   = useState([]);
//   const [sessionId, setSessionId] = useState("");

//   // 1. 页面加载时创建 chat 会话
//   useEffect(() => {
//     newSession()
//       .then(res => setSessionId(res.data.session_id))
//       .catch(err => {
//         console.error("创建会话失败", err);
//         alert("无法创建对话会话，请检查网络或重新登录");
//       });
//   }, []);

//   /** 文字消息 */
//   const handleSend = async (text) => {
//     if (!text.trim() || !sessionId) return;
//     // 1) 本地渲染用户文字
//     setMessages(prev => [
//       ...prev,
//       { type: "text", content: text.trim(), sender: "user" },
//     ]);
//     // 2) 调用后端
//     try {
//       const res = await sendMessage(sessionId, { text });
//       setMessages(prev => [
//         ...prev,
//         { type: "text", content: res.data.answer, sender: "bot" },
//       ]);
//     } catch (err) {
//       console.error("文字消息发送失败", err);
//       alert(err.response?.data?.error || "文字消息发送失败");
//     }
//   };

//   /** 图片消息 */
//   const handleImageUpload = async (file) => {
//     if (!file || !sessionId) return;
//     // 1) 本地预览
//     const previewUrl = URL.createObjectURL(file);
//     setMessages(prev => [
//       ...prev,
//       { type: "image", content: previewUrl, sender: "user" },
//     ]);
//     // 2) 上传图片到后端，拿到 image_url
//     let imageUrl;
//     try {
//       const upRes = await uploadImage(file);
//       imageUrl = upRes.data.image_url; // e.g. "/uploads/xxx.jpg"
//     } catch (err) {
//       console.error("图片上传失败", err);
//       return alert(err.response?.data?.error || "图片上传失败");
//     }
//     // 3) 调用聊天接口
//     try {
//       const res = await sendMessage(sessionId, { imageUrl });
//       setMessages(prev => [
//         ...prev,
//         { type: "text", content: res.data.answer, sender: "bot" },
//       ]);
//     } catch (err) {
//       console.error("图片消息发送失败", err);
//       alert(err.response?.data?.error || "图片消息发送失败");
//     }
//   };

//   return (
//     <div className="app-container">
//       <Sidebar />
//       <MainArea
//         messages={messages}
//         onSend={handleSend}
//         onImageUpload={handleImageUpload}
//       />
//     </div>
//   );
// }

// export default App;


// File: src/App.js
// -------------------------0508
// import React, { useState } from "react";
// import Sidebar from "./components/Sidebar";
// import MainArea from "./components/MainArea";
// import { createSession, sendMessage } from "./api/chat";
// import { uploadImage } from "./api/upload";
// import "./App.css";

// function App() {
//   const [messages, setMessages]   = useState([]);
//   const [sessionId, setSessionId] = useState("");

//   const handleSend = async (text, file) => {
//     if (!text.trim() && !file) return;

//     if (!localStorage.getItem("access_token")) {
//       return alert("请先登录");
//     }

//     if (!sessionId) {
//       try {
//         const id = await createSession();
//         setSessionId(id);
//       } catch (err) {
//         console.error("创建会话失败", err);
//         return alert("无法创建对话会话，请稍后重试");
//       }
//     }

//     if (text.trim()) {
//       setMessages(prev => [
//         ...prev,
//         { type: "text", content: text.trim(), sender: "user" },
//       ]);
//     }

//     let image_path;
//     if (file) {
//       setMessages(prev => [
//         ...prev,
//         { type: "image", content: URL.createObjectURL(file), sender: "user" },
//       ]);

//       try {
//         const upRes = await uploadImage(file);
//         image_path = upRes.data.image_url;
//       } catch (err) {
//         console.error("图片上传失败", err);
//         return alert(err.response?.data?.error || "图片上传失败");
//       }
//     }

//     try {
//       const { answer } = await sendMessage(sessionId, { question: text.trim(), image_path });
//       setMessages(prev => [
//         ...prev,
//         { type: "text", content: answer, sender: "bot" },
//       ]);
//     } catch (err) {
//       console.error("消息发送失败", err);
//       alert(err.response?.data?.error || "消息发送失败");
//     }
//   };

//   return (
//     <div className="app-container">
//       <Sidebar />
//       <MainArea messages={messages} onSend={handleSend} />
//     </div>
//   );
// }

// export default App;



// File: src/App.js
// import React, { useState } from "react";
// import Sidebar from "./components/Sidebar";
// import MainArea from "./components/MainArea";
// import { createSession } from "./api/chat";
// import "./App.css";

// function App() {
//   const [messages, setMessages] = useState([]);
//   const [sessionId, setSessionId] = useState("");
//   const [hasSession, setHasSession] = useState(false);

//   const handleSend = async (text, file) => {
//     if (!text.trim() && !file) return;

//     if (!sessionId) {
//       try {
//         const id = await createSession();
//         setSessionId(id);
//         setHasSession(true);
//       } catch (err) {
//         console.error("创建会话失败", err);
//         return alert("无法创建对话会话，请稍后重试");
//       }
//     }

//     if (text.trim()) {
//       setMessages(prev => [
//         ...prev,
//         { type: "text", content: text.trim(), sender: "user" },
//       ]);
//     }

//     if (file) {
//       setMessages(prev => [
//         ...prev,
//         { type: "image", content: URL.createObjectURL(file), sender: "user" },
//       ]);
//     }

//     // 这里添加发送消息的逻辑
//   };

//   return (
//     <div className="app-container">
//       <Sidebar />
//       <MainArea
//         messages={messages}
//         onSend={handleSend}
//         hasSession={hasSession}
//       />
//     </div>
//   );
// }

// export default App;


// src/App.js
import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import MainArea from "./components/MainArea";
import { createSession, sendMessage } from "./api/chat";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState("");

  const handleSend = async (text, file) => {
    if (!text.trim() && !file) return;

    // 创建会话
    if (!sessionId) {
      try {
        const id = await createSession();
        setSessionId(id);
      } catch (err) {
        console.error("创建会话失败", err);
        return alert("无法创建对话会话，请稍后重试");
      }
    }

    // 本地展示用户消息
    if (text.trim()) {
      setMessages(prev => [...prev, { type: "text", content: text.trim(), sender: "user" }]);
    }
    if (file) {
      setMessages(prev => [...prev, { type: "image", content: URL.createObjectURL(file), sender: "user" }]);
    }

    // 发送到后端
    try {
      const payload = {
        question: text.trim() || undefined,
        image_url: file ? URL.createObjectURL(file) : undefined
      };
      const res = await sendMessage(sessionId, payload);
      setMessages(prev => [...prev, { type: "text", content: res.answer, sender: "bot" }]);
    } catch (err) {
      console.error("发送消息失败", err);
      alert("消息发送失败，请重试");
    }
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




