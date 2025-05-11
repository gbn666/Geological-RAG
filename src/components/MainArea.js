// src/components/MainArea.js0511
import React from "react";
import "./MainArea.css";
import HeaderIntro from "./HeaderIntro";
import ChatHistory from "./ChatHistory";
import ChatInput from "./ChatInput";

export default function MainArea({ messages, onSend, hasMessage }) {
  return (
    <div className={`main-area ${hasMessage ? "chatting" : "centered"}`}>
      {!hasMessage && <HeaderIntro />}

      {hasMessage && (
        <>
          <HeaderIntro isFixed />

          {/* 外层：铺满宽度，带滚动条 */}
          <div className="messages-outer">
            {/* 内层：限制最大宽度，居中 */}
            <div className="messages-inner">
              <ChatHistory messages={messages} />
            </div>
          </div>
        </>
      )}

      <ChatInput onSend={onSend} />
    </div>
  );
}



