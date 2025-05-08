//MainArea.js
// import React from "react";
// import "./MainArea.css";
// import HeaderIntro from "./HeaderIntro";
// import ChatInput from "./ChatInput";

// export default function MainArea() {
//   return (
//     <div className="main-area">
//       <HeaderIntro />
//       <ChatInput />
//     </div>
//   );
// }

// src/components/MainArea.js
// import React from "react";
// import "./MainArea.css";
// import HeaderIntro from "./HeaderIntro";
// import ChatInput from "./ChatInput";

// export default function MainArea({ messages, onSend }) {
//   return (
//     <div className="main-area">
//       <HeaderIntro />

//       {/* 消息列表 */}
//       <div className="messages-container">
//         {messages.map((msg, idx) => (
//           <div key={idx} className={`message-bubble ${msg.sender}`}>
//             {msg.type === "text" && <p>{msg.content}</p >}
//             {msg.type === "image" && (
//               <img
//                 src={msg.content}
//                 alt="用户上传"
//                 className="message-image"
//               />
//             )}
//           </div>
//         ))}
//       </div>

//       {/* 输入框：传入 onSend 回调 */}
//       <ChatInput onSend={onSend} />
//     </div>
//   );
// }





// src/components/MainArea.js
// import React from "react";
// import "./MainArea.css";
// import HeaderIntro from "./HeaderIntro";
// import ChatInput from "./ChatInput";

// export default function MainArea({ messages, onSend }) {
//   return (
//     <div className="main-area">
//       <HeaderIntro />

//       {/* 消息列表 */}
//       <div className="messages-container">
//         {messages.map((msg, idx) => (
//           <div key={idx} className={`message-bubble ${msg.sender}`}>
//             {msg.type === "text" && <p>{msg.content}</p>}
//             {msg.type === "image" && (
//               <img
//                 src={msg.content}
//                 alt="用户上传"
//                 className="message-image"
//               />
//             )}
//           </div>
//         ))}
//       </div>

//       {/* 输入框：直接传 onSend(text, file) */}
//       <ChatInput onSend={onSend} />
//     </div>
//   );
// }




// File: src/components/MainArea.js0508
// import React from "react";
// import "./MainArea.css";
// import HeaderIntro from "./HeaderIntro";
// import ChatInput from "./ChatInput";

// export default function MainArea({ messages, onSend, hasMessage }) {
//   return (
//     <div className={`main-area ${hasMessage ? "chatting" : "centered"}`}>
//       <HeaderIntro />

//       {hasMessage && (
//         <div className="messages-container">
//           {messages.map((msg, idx) => (
//             <div key={idx} className={`message-bubble ${msg.sender}`}>
//               {msg.type === "text" && <p>{msg.content}</p>}
//               {msg.type === "image" && (
//                 <img
//                   src={msg.content}
//                   alt="用户上传"
//                   className="message-image"
//                 />
//               )}
//             </div>
//           ))}
//         </div>
//       )}

//       <ChatInput onSend={onSend} />
//     </div>
//   );
// }




// src/components/MainArea.js
import React from "react";
import "./MainArea.css";
import HeaderIntro from "./HeaderIntro";
import ChatInput from "./ChatInput";

export default function MainArea({ messages, onSend, hasMessage }) {
  return (
    <div className={`main-area ${hasMessage ? "chatting" : "centered"}`}>
      <HeaderIntro />

      {hasMessage && (
        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.sender}`}>
              {msg.type === "text" ? (
                <p>{msg.content}</p>
              ) : (
                <img src={msg.content} alt="用户上传" className="message-image" />
              )}
            </div>
          ))}
        </div>
      )}

      <ChatInput onSend={onSend} />
    </div>
  );
}

