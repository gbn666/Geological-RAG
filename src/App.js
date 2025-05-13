// // // File: src/App.js0511
// // import React, { useState } from "react";
// // import Sidebar from "./components/Sidebar";
// // import MainArea from "./components/MainArea";
// // import { createSession, sendMessage } from "./api/chat";
// // import { uploadImage } from "./api/upload";
// // import "./App.css";

// // function App() {
// //   const [messages, setMessages] = useState([]);
// //   const [sessionId, setSessionId] = useState("");

// //   // onSend 会返回一个 Promise，ChatInput 可以 await 它
// //   const handleSend = async (text, file) => {
// //     if (!text.trim() && !file) {
// //       throw new Error("请输入文字或选择图片");
// //     }

// //     // —— 按需创建会话 —— 
// //     let sid = sessionId;
// //     if (!sid) {
// //       sid = await createSession();
// //       setSessionId(sid);
// //     }

// //     // —— Optimistic UI 渲染用户消息 —— 
// //     const userMsgs = [];
// //     const trimmed = text.trim();
// //     if (trimmed) {
// //       userMsgs.push({ type: "text", content: trimmed, sender: "user" });
// //     }
// //     let previewUrl;
// //     if (file) {
// //       previewUrl = URL.createObjectURL(file);
// //       userMsgs.push({ type: "image", content: previewUrl, sender: "user" });
// //     }
// //     setMessages(prev => [...prev, ...userMsgs]);

// //     // —— 上传图片（可选） —— 
// //     let imageUrl;
// //     if (file) {
// //       try {
// //         const resp = await uploadImage(file);
// //         imageUrl = resp.data.image_url;
// //       } catch {
// //         // 上传失败就用本地预览也能继续
// //         imageUrl = previewUrl;
// //       }
// //     }

// //     // —— 调用后端接口 —— 
// //     const res = await sendMessage(sid, {
// //       question: trimmed || undefined,
// //       imageUrl,
// //     });

// //     // —— 渲染机器人回复 —— 
// //     setMessages(prev => [
// //       ...prev,
// //       { type: "text", content: res.answer, sender: "bot" },
// //     ]);
// //     return res;
// //   };

// //   return (
// //     <div className="app-container">
// //       <Sidebar />
// //       <MainArea
// //         messages={messages}
// //         onSend={handleSend}
// //         hasMessage={messages.length > 0}
// //       />
// //     </div>
// //   );
// // }

// // export default App;




// // File: src/App.js
// import React, { useState } from "react";
// import Sidebar from "./components/Sidebar";
// import MainArea from "./components/MainArea";
// import { createSession, sendMessage } from "./api/chat";
// import { uploadImage } from "./api/upload";
// import "./App.css";

// function App() {
//   const [messages, setMessages]   = useState([]);   // 当前会话消息
//   const [sessionId, setSessionId] = useState("");   // 当前会话 ID
//   const [sessions, setSessions]   = useState([]);   // 已有会话列表：{ sessionId, title }

//   // 点击“新对话”：清空当前会话（重新开始）
//   const handleNewChat = () => {
//     setSessionId("");
//     setMessages([]);
//   };

//   // 发送消息
//   const handleSend = async (text, file) => {
//     if (!text.trim() && !file) {
//       throw new Error("请输入文字或选择图片");
//     }

//     const trimmed = text.trim();
//     // —— 按需创建会话 —— 
//     let sid = sessionId;
//     if (!sid) {
//       sid = await createSession();
//       setSessionId(sid);
//     }

//     // —— 如果这是该会话的第一条用户提问，记录到 sessions 列表 —— 
//     setSessions(prev => {
//       const exists = prev.find(s => s.sessionId === sid);
//       if (!exists) {
//         return [{ sessionId: sid, title: trimmed || "[图片消息]" }, ...prev];
//       }
//       return prev;
//     });

//     // —— Optimistic UI 渲染用户消息 —— 
//     const userMsgs = [];
//     if (trimmed) {
//       userMsgs.push({ type: "text", content: trimmed, sender: "user" });
//     }
//     let previewUrl;
//     if (file) {
//       previewUrl = URL.createObjectURL(file);
//       userMsgs.push({ type: "image", content: previewUrl, sender: "user" });
//     }
//     setMessages(prev => [...prev, ...userMsgs]);

//     // —— 上传图片（可选） —— 
//     let imageUrl;
//     if (file) {
//       try {
//         const resp = await uploadImage(file);
//         imageUrl = resp.data.image_url;
//       } catch {
//         imageUrl = previewUrl;
//       }
//     }

//     // —— 调用后端接口 —— 
//     const res = await sendMessage(sid, {
//       question: trimmed || undefined,
//       imageUrl,
//     });

//     // —— 渲染机器人回复 —— 
//     setMessages(prev => [
//       ...prev,
//       { type: "text", content: res.answer, sender: "bot" },
//     ]);
//     return res;
//   };

//   // 切换会话：把该会话的消息清空（或可从后端拉历史）
//   const handleSelectSession = (sid) => {
//     setSessionId(sid);
//     setMessages([]);  // 如果需要，可改为拉取历史
//   };

//   return (
//     <div className="app-container">
//       <Sidebar
//         sessions={sessions}
//         current={sessionId}
//         onNew={handleNewChat}
//         onSelect={handleSelectSession}
//       />
//       <MainArea
//         messages={messages}
//         onSend={handleSend}
//         hasMessage={messages.length > 0}
//       />
//     </div>
//   );
// }

// export default App;
// File: src/App.js
// File: src/App.js
// import React, { useState } from "react";
// import Sidebar from "./components/Sidebar";
// import MainArea from "./components/MainArea";
// import { createSession, sendMessage, listSessions } from "./api/chat";
// import { uploadImage } from "./api/upload";
// import "./App.css";

// function App() {
//   const [messages, setMessages]   = useState([]);  // 当前会话消息
//   const [sessionId, setSessionId] = useState("");  // 当前会话 ID

//   // 新对话：清空
//   const handleNewChat = () => {
//     setSessionId("");
//     setMessages([]);
//   };

//   // 切换历史会话：拉历史
//   const handleSelectSession = async sid => {
//     setSessionId(sid);
//     try {
//       const history = await  listSessions(sid);
//       setMessages(history);
//     } catch (err) {
//       console.error("拉取历史消息失败", err);
//       setMessages([]);
//     }
//   };

//   // 发送消息
//   const handleSend = async (text, file) => {
//     if (!text.trim() && !file) {
//       throw new Error("请输入文字或选择图片");
//     }

//     let sid = sessionId;
//     if (!sid) {
//       sid = await createSession();
//       setSessionId(sid);
//     }

//     // Optimistic UI：用户消息
//     const temp = [];
//     if (text.trim()) temp.push({ type: "text", content: text.trim(), sender: "user" });
//     if (file) {
//       const preview = URL.createObjectURL(file);
//       temp.push({ type: "image", content: preview, sender: "user" });
//     }
//     setMessages(prev => [...prev, ...temp]);

//     // 上传图片（如有）
//     let imageUrl;
//     if (file) {
//       try {
//         // 假设有 uploadImage API
//         const resp = await uploadImage(file);
//         imageUrl = resp.data.image_url;
//       } catch {
//         imageUrl = temp.find(m => m.type === "image").content;
//       }
//     }

//     // 后端发送
//     const res = await sendMessage(sid, {
//       question: text.trim() || undefined,
//       imageUrl,
//     });

//     // 渲染机器人回复
//     setMessages(prev => [
//       ...prev,
//       { type: "text", content: res.answer, sender: "bot" }
//     ]);

//     return res;
//   };

//   return (
//     <div className="app-container">
//       <Sidebar
//         onNew={handleNewChat}
//         onSelect={handleSelectSession}
//         currentSessionId={sessionId}
//       />
//       <MainArea
//         messages={messages}
//         onSend={handleSend}
//         hasMessage={messages.length > 0}
//       />
//     </div>
//   );
// }

// export default App;




import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import MainArea from "./components/MainArea";
import { createSession, sendMessage, getSessionHistory, listSessions } from "./api/chat";
import { uploadImage } from "./api/upload";
import "./App.css";

function App() {
  const [messages, setMessages]   = useState([]);  // 当前会话消息
  const [sessionId, setSessionId] = useState("");  // 当前会话 ID

  // 新对话：清空
  const handleNewChat = () => {
    setSessionId("");
    setMessages([]);
  };

  // 切换历史会话：拉历史
  const handleSelectSession = async sid => {
    setSessionId(sid);
    try {
      const history = await getSessionHistory(sid);
      const filtered = history.filter(msg => msg.type !== "image");
      setMessages(filtered);
    } catch (err) {
      console.error("拉取历史消息失败", err);
      setMessages([]);
    }
  };

  // 发送消息
  const handleSend = async (text, file) => {
    if (!text.trim() && !file) {
      throw new Error("请输入文字或选择图片");
    }

    let sid = sessionId;
    if (!sid) {
      sid = await createSession();
      setSessionId(sid);
    }

    // Optimistic UI：用户消息
    const temp = [];
    if (text.trim()) temp.push({ type: "text", content: text.trim(), sender: "user" });
    if (file) {
      const preview = URL.createObjectURL(file);
      temp.push({ type: "image", content: preview, sender: "user" });
    }
    setMessages(prev => [...prev, ...temp]);

    // 上传图片（如有）
    let imageUrl;
    if (file) {
      try {
        const resp = await uploadImage(file);
        imageUrl = resp.data.image_url;
        // 可选：替换 blob URL 为真实地址
        setMessages(prev =>
          prev.map(msg =>
            msg.type === "image" && msg.content === URL.createObjectURL(file)
              ? { ...msg, content: imageUrl }
              : msg
          )
        );
      } catch (err) {
        console.error("图片上传失败", err);
        imageUrl = undefined;
      }
    }

    // 后端发送
    const res = await sendMessage(sid, {
      question: text.trim() || undefined,
      imageUrl,
    });

    // 渲染机器人回复
    setMessages(prev => [
      ...prev,
      { type: "text", content: res.answer, sender: "bot" }
    ]);

    return res;
  };

  return (
    <div className="app-container">
      <Sidebar
        onNew={handleNewChat}
        onSelect={handleSelectSession}
        currentSessionId={sessionId}
      />
      <MainArea
        messages={messages}
        onSend={handleSend}
        hasMessage={messages.length > 0}
      />
    </div>
  );
}

export default App;
