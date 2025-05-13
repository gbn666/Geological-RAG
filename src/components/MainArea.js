// // src/components/MainArea.js0511
// import React from "react";
// import "./MainArea.css";
// import HeaderIntro from "./HeaderIntro";
// import ChatHistory from "./ChatHistory";
// import ChatInput from "./ChatInput";

// export default function MainArea({ messages, onSend, hasMessage }) {
//   return (
//     <div className={`main-area ${hasMessage ? "chatting" : "centered"}`}>
//       {!hasMessage && <HeaderIntro />}

//       {hasMessage && (
//         <>
//           <HeaderIntro isFixed />

//           {/* 外层：铺满宽度，带滚动条 */}
//           <div className="messages-outer">
//             {/* 内层：限制最大宽度，居中 */}
//             <div className="messages-inner">
//               <ChatHistory messages={messages} />
//             </div>
//           </div>
//         </>
//       )}

//       <ChatInput onSend={onSend} />
//     </div>
//   );
// }



// // File: src/components/MainArea.js
// import React from "react";
// import "./MainArea.css";
// import HeaderIntro from "./HeaderIntro";
// import ChatHistory from "./ChatHistory";
// import ChatInput from "./ChatInput";

// export default function MainArea({ messages, onSend, hasMessage }) {
//   return (
//     <div className={`main-area ${hasMessage ? "chatting" : "centered"}`}>
//       {!hasMessage && <HeaderIntro />}

//       {hasMessage && (
//         <>
//           <HeaderIntro isFixed />
//           <div className="messages-outer">
//             <div className="messages-inner">
//               <ChatHistory messages={messages} />
//             </div>
//           </div>
//         </>
//       )}

//       <ChatInput onSend={onSend} />
//     </div>
//   );
// }


// File: src/components/MainArea.js
import React, { useEffect, useRef } from "react";
import "./MainArea.css";
import HeaderIntro from "./HeaderIntro";
import ChatHistory from "./ChatHistory";
import ChatInput from "./ChatInput";

export default function MainArea({
  messages,
  onSend,
  hasMessage,
  loadingHistory = false,  // 来自父组件，表示是否正在拉取历史消息
}) {
  const endRef = useRef(null);

  // 每当 messages 更新且不在加载中，就滚动到底部
  useEffect(() => {
    if (!loadingHistory && endRef.current) {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loadingHistory]);

  return (
    <div className={`main-area ${hasMessage ? "chatting" : "centered"}`}>
      {/* 初始状态或者没有历史 & 新对话时显示引导 */}
      {!hasMessage && !loadingHistory && <HeaderIntro />}

      {/* 加载历史时的提示 */}
      {loadingHistory && (
        <div className="history-loading">正在加载历史消息…</div>
      )}

      {/* 正常聊天区 */}
      {hasMessage && !loadingHistory && (
        <>
          <HeaderIntro isFixed />
          <div className="messages-outer">
            <div className="messages-inner">
              <ChatHistory messages={messages} />
              {/* 这个空 div 用于滚动到底部 */}
              <div ref={endRef} />
            </div>
          </div>
        </>
      )}

      {/* 输入框永远可见 */}
      <ChatInput onSend={onSend} />
    </div>
  );
}

