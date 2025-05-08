// // 修改后的 src/components/ChatInput.js
// src/components/ChatInput.js
// import React, { useState } from "react";
// import "./ChatInput.css";
// import attachIcon from "../assets/attachIcon.svg";
// import sendIcon from "../assets/sendIcon.svg";
// import { uploadImage } from "../api/upload";
// import { sendMessage } from "../api/chat"; // ✅ 新增

// export default function ChatInput({ sessionId, onResponse = () => {} }) { // ✅ 接收 sessionId
//   const [text, setText] = useState("");
//   const [file, setFile] = useState(null);
//   const [preview, setPreview] = useState(null);

//   const handleTextChange = (e) => setText(e.target.value);

//   const handleFileChange = (e) => {
//     const selected = e.target.files[0];
//     if (selected && ["image/jpeg", "image/png", "image/jpg"].includes(selected.type)) {
//       setFile(selected);
//       setPreview(URL.createObjectURL(selected));
//     } else {
//       alert("请选择 jpg / jpeg / png 格式的图片");
//       setFile(null);
//       setPreview(null);
//     }
//   };

//   const handleRemoveImage = () => {
//     setFile(null);
//     setPreview(null);
//   };

//   const handleSend = async () => {
//     let imageUrl = "";
//     if (file) {
//       try {
//         const res = await uploadImage(file);
//         imageUrl = res.data.image_url;
//       } catch (err) {
//         console.error(err);
//         alert(err.response?.data?.error || "图片上传失败");
//         return;
//       } finally {
//         handleRemoveImage();
//       }
//     }

//     if (!text.trim() && !imageUrl) {
//       alert("请输入内容或选择图片");
//       return;
//     }

//     try {
//       const res = await sendMessage({
//         sessionId,
//         text,
//         imageUrl,
//       });

//       onResponse(res); // ✅ 回调返回结果（可用于渲染）
//       setText(""); // 清空文本框
//     } catch (err) {
//       console.error("发送失败：", err.message);
//       alert("发送失败，请检查网络或登录状态");
//     }
//   };

//   return (
//     <div className="chat-input">
//       <textarea
//         placeholder="说出你的疑问"
//         className="chat-input-textarea"
//         value={text}
//         onChange={handleTextChange}
//       />

//       {preview && (
//         <div className="preview-container">
//           <img src={preview} alt="预览" className="preview-image" />
//           <button type="button" className="remove-image-btn" onClick={handleRemoveImage}>
//             ×
//           </button>
//         </div>
//       )}

//       <div className="chat-buttons">
//         {!file && (
//           <label className="attach-btn">
//             <img src={attachIcon} alt="添加附件" />
//             <span>上传文件</span>
//             <input
//               type="file"
//               accept=".jpg,.jpeg,.png"
//               style={{ display: "none" }}
//               onChange={handleFileChange}
//             />
//           </label>
//         )}
//         <button className="send-btn" onClick={handleSend}>
//           <img src={sendIcon} alt="发送" />
//           <span>发送</span>
//         </button>
//       </div>
//     </div>
//   );
// }


// // src/components/ChatInput.js
// // src/components/ChatInput.js
// import React, { useState } from 'react';
// import './ChatInput.css';
// import attachIcon from '../assets/attachIcon.svg';
// import sendIcon   from '../assets/sendIcon.svg';

// export default function ChatInput({ onSend }) {
//   const [text, setText]       = useState('');
//   const [file, setFile]       = useState(null);
//   const [preview, setPreview] = useState(null);

//   // 文本变化
//   const handleTextChange = e => {
//     setText(e.target.value);
//   };

//   // 选中图片
//   const handleFileChange = e => {
//     const selected = e.target.files[0];
//     if (selected && ['image/jpeg','image/png','image/jpg'].includes(selected.type)) {
//       setFile(selected);
//       setPreview(URL.createObjectURL(selected));
//     } else {
//       alert('仅支持 jpg / jpeg / png 格式');
//       setFile(null);
//       setPreview(null);
//     }
//   };

//   // 删除已选图片
//   const handleRemoveImage = () => {
//     setFile(null);
//     setPreview(null);
//   };

//   // 发送文字 + 可选图片
//   const handleSend = () => {
//     if (!text.trim() && !file) return;  // 空消息不发
//     onSend(text.trim(), file);
//     setText('');
//     setFile(null);
//     setPreview(null);
//   };

//   return (
//     <div className="chat-input">
//       <textarea
//         className="chat-input-textarea"
//         placeholder="说出你的疑问"
//         value={text}
//         onChange={handleTextChange}
//       />

//       {/* 图片预览 */}
//       {preview && (
//         <div className="preview-container">
//           <img src={preview} alt="预览" className="preview-image" />
//           <button
//             type="button"
//             className="remove-image-btn"
//             onClick={handleRemoveImage}
//           >
//             ×
//           </button>
//         </div>
//       )}

//       <div className="chat-buttons">
//         {/* 上传按钮（仅在还没选图片时显示） */}
//         {!file && (
//           <label className="attach-btn">
//             <img src={attachIcon} alt="上传图片" />
//             <span>上传图片</span>
//             <input
//               type="file"
//               accept=".jpg,.jpeg,.png"
//               style={{ display: 'none' }}
//               onChange={handleFileChange}
//             />
//           </label>
//         )}

//         {/* 发送按钮 */}
//         <button className="send-btn" onClick={handleSend}>
//           <img src={sendIcon} alt="发送" />
//           <span>发送</span>
//         </button>
//       </div>
//     </div>
    
//   );
  
// }


// // src/components/ChatInput.js
// import React, { useState, useEffect } from 'react';
// import './ChatInput.css';
// import attachIcon from '../assets/attachIcon.svg';
// import sendIcon   from '../assets/sendIcon.svg';
// import { createSession, sendMessage } from '../api/chat';
// import { uploadImage } from '../api/upload';

// export default function ChatInput() {
//   const [sessionId, setSessionId] = useState(null);
//   const [loadingSession, setLoadingSession] = useState(true);
//   const [text, setText] = useState('');
//   const [file, setFile] = useState(null);
//   const [preview, setPreview] = useState(null);
//   const [messages, setMessages] = useState([]);
//   const [sending, setSending] = useState(false);

//   // 初始化 Session
//   useEffect(() => {
//     (async () => {
//       try {
//         const sid = await createSession();
//         setSessionId(sid);
//       } catch (err) {
//         console.error('创建会话失败', err);
//       } finally {
//         setLoadingSession(false);
//       }
//     })();
//   }, []);

//   const handleTextChange = e => setText(e.target.value);

//   const handleFileChange = e => {
//     const f = e.target.files[0];
//     if (f && (f.type === 'image/jpeg' || f.type === 'image/png')) {
//       setFile(f);
//       setPreview(URL.createObjectURL(f));
//     } else {
//       alert('只支持 jpg/png 图片');
//       setFile(null);
//       setPreview(null);
//     }
//   };

//   const handleRemoveImage = () => {
//     if (sending) return;
//     setFile(null);
//     setPreview(null);
//   };

//   const handleSend = async () => {
//     const q = text.trim();
//     if ((!q && !file) || loadingSession || sending) return;

//     // 先把用户消息放进列表
//     setMessages(m => [...m, { sender: 'user', text: q, image: preview }]);
//     setText('');
//     setFile(null);
//     setPreview(null);
//     setSending(true);

//     try {
//       let imageUrl = null;
//       if (file) {
//         // 1) 上传图片
//         const up = await uploadImage(file);
//         imageUrl = up.data.url;
//       }
//       // 2) 发送问答请求
//       const data = await sendMessage(sessionId, { question: q, image_url:imageUrl });
//       setMessages(m => [
//         ...m,
//         { sender: 'bot', text: data.answer, candidates: data.kg_candidates }
//       ]);
//     } catch (err) {
//       console.error('发送失败', err);
//       alert('发送出错，请重试');
//     } finally {
//       setSending(false);
//     }
//   };

//   const disabledInput = loadingSession || sending;
//   const canSend = !disabledInput && (text.trim() || file);

//   return (
//     <div className="chat-input-container">
//       {loadingSession && <div className="session-loading">正在初始化会话…</div>}
//       <div className="chat-history">
//         {messages.map((msg, i) => (
//           <div key={i} className={`chat-message ${msg.sender}-msg`}>
//             {msg.image && <img src={msg.image} className="message-image" alt="" />}
//             <div className="message-text">{msg.text}</div>
//             {msg.sender === 'bot' && msg.candidates && (
//               <ul className="message-candidates">
//                 {msg.candidates.map(c => (
//                   <li key={c.name}>
//                     <strong>{c.name}</strong>（{(c.prob*100).toFixed(1)}%）：{c.kg_info}
//                   </li>
//                 ))}
//               </ul>
//             )}
//           </div>
//         ))}
//       </div>

//       <div className="chat-input">
//         <textarea
//           value={text}
//           onChange={handleTextChange}
//           disabled={disabledInput}
//           placeholder={disabledInput ? '请稍候…' : '输入你的问题…'}
//           className="chat-input-textarea"
//         />

//         {preview && (
//           <div className="preview-container">
//             <img src={preview} className="preview-image" alt="上传文件" />
//             <button onClick={handleRemoveImage} disabled={sending} className="remove-image-btn">
//               ×
//             </button>
//           </div>
//         )}

//         <div className="chat-buttons">
//           {!file && !loadingSession && !sending && (
//             <label className="attach-btn">
//               <img src={attachIcon} alt="" />
//               <input type="file" accept="image/*" onChange={handleFileChange} hidden />
//             </label>
//           )}
//           <button
//             onClick={handleSend}
//             disabled={!canSend}
//             className="send-btn"
//           >
//             <img src={sendIcon} alt="发送" />
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

// src/components/ChatInput.js0507
// import React, { useState } from 'react';
// import './ChatInput.css';
// import attachIcon from '../assets/attachIcon.svg'; // 使用指定的图标文件
// import sendIcon from '../assets/sendIcon.svg'; // 使用指定的图标文件

// export default function ChatInput({ onSend }) {
//   const [text, setText] = useState('');
//   const [file, setFile] = useState(null);
//   const [preview, setPreview] = useState(null);

//   const handleTextChange = e => setText(e.target.value);

//   const handleFileChange = e => {
//     const selected = e.target.files[0];
//     if (selected && ['image/jpeg', 'image/png'].includes(selected.type)) {
//       setFile(selected);
//       setPreview(URL.createObjectURL(selected));
//     } else {
//       alert('仅支持 jpg/png 格式');
//       setFile(null);
//       setPreview(null);
//     }
//   };

//   const handleRemoveImage = () => {
//     setFile(null);
//     setPreview(null);
//   };

//   const handleSend = () => {
//     if (!text.trim() && !file) return;
//     onSend(text.trim(), file);
//     setText('');
//     setFile(null);
//     setPreview(null);
//   };

//   return (
//     <div className="chat-input">
//       <textarea
//         className="chat-input-textarea"
//         placeholder="说出你的疑问"
//         value={text}
//         onChange={handleTextChange}
//       />

//       {preview && (
//         <div className="preview-container">
//           <img src={preview} alt="预览" className="preview-image" />
//           <button type="button" className="remove-image-btn" onClick={handleRemoveImage}>
//             ×
//           </button>
//         </div>
//       )}

//       <div className="chat-buttons">
//         {!file && (
//           <label className="attach-btn">
//             <img src={attachIcon} alt="上传文件" />
//             <span>上传文件</span>
//             <input
//               type="file"
//               accept="image/*"
//               style={{ display: 'none' }}
//               onChange={handleFileChange}
//             />
//           </label>
//         )}
//         <button className="send-btn" onClick={handleSend}>
//           <img src={sendIcon} alt="发送" />
//           <span>发送</span>
//         </button>
//       </div>
//     </div>
//   );
// }



// src/components/ChatInput.js0508
import React, { useState, useEffect, useRef } from 'react';
import './ChatInput.css';
import attachIcon from '../assets/attachIcon.svg';
import sendIcon   from '../assets/sendIcon.svg';
import { createSession, sendMessage } from '../api/chat';
import { uploadImage } from '../api/upload';

export default function ChatInput() {
  const [sessionId, setSessionId]       = useState(null);
  const [loadingSession, setLoadingSession] = useState(true);
  const [text, setText]                 = useState('');
  const [file, setFile]                 = useState(null);
  const [preview, setPreview]           = useState(null);
  const [messages, setMessages]         = useState([]);
  const [sending, setSending]           = useState(false);
  const historyEndRef = useRef(null);

  // 初始化 Session
  useEffect(() => {
    (async () => {
      try {
        const sid = await createSession();
        setSessionId(sid);
      } catch (err) {
        console.error('创建会话失败', err);
        alert('无法初始化会话，请重试');
      } finally {
        setLoadingSession(false);
      }
    })();
  }, []);

  // 滚动到底部
  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleTextChange = e => setText(e.target.value);

  const handleFileChange = e => {
    const selected = e.target.files[0];
    if (selected && ['image/jpeg', 'image/png'].includes(selected.type)) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    } else {
      alert('仅支持 jpg/png 格式');
      setFile(null);
      setPreview(null);
    }
  };

  const handleRemoveImage = () => {
    if (sending) return;
    setFile(null);
    setPreview(null);
  };

  const handleSend = async () => {
    const q = text.trim();
    if ((!q && !file) || loadingSession || sending) return;

    // 将用户消息先展示到列表
    setMessages(m => [...m, { sender: 'user', text: q, image: preview }]);
    setText('');
    setFile(null);
    setPreview(null);
    setSending(true);

    try {
      let imageUrl = null;
      if (file) {
        // 上传图片
        const up = await uploadImage(file);
        imageUrl = up.data.url;
      }
      // 发送问答请求
      const res = await sendMessage(sessionId, { question: q, image_url: imageUrl });
      setMessages(m => [
        ...m,
        { sender: 'bot', text: res.answer, candidates: res.kg_candidates }
      ]);
    } catch (err) {
      console.error('发送失败', err);
      alert('发送出错，请重试');
    } finally {
      setSending(false);
    }
  };

  const disabledInput = loadingSession || sending;
  const canSend = !disabledInput && (text.trim() || file);

  return (
    <div className="chat-input-container">
      {loadingSession && <div className="session-loading">正在初始化会话…</div>}

      <div className="chat-history">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.sender}-msg`}>
            {msg.image && <img src={msg.image} className="message-image" alt="用户上传" />}
            <div className="message-text">{msg.text}</div>
            {msg.sender === 'bot' && msg.candidates && (
              <ul className="message-candidates">
                {msg.candidates.map(c => (
                  <li key={c.name}>
                    <strong>{c.name}</strong>（{(c.prob * 100).toFixed(1)}%）
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        <div ref={historyEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          className="chat-input-textarea"
          placeholder={disabledInput ? '请稍候…' : '说出你的疑问'}
          value={text}
          onChange={handleTextChange}
          disabled={disabledInput}
        />

        {preview && (
          <div className="preview-container">
            <img src={preview} alt="预览" className="preview-image" />
            <button
              type="button"
              className="remove-image-btn"
              onClick={handleRemoveImage}
              disabled={sending}
            >
              ×
            </button>
          </div>
        )}

        <div className="chat-buttons">
          {!file && !loadingSession && !sending && (
            <label className="attach-btn">
              <img src={attachIcon} alt="上传文件" />
              <span>上传文件</span>
              <input
                type="file"
                accept="image/png, image/jpeg"
                hidden
                onChange={handleFileChange}
              />
            </label>
          )}
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!canSend}
          >
            <img src={sendIcon} alt="发送" />
            <span>发送</span>
          </button>
        </div>
      </div>
    </div>
);
}







