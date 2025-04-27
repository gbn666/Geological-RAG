//ChatInput.js
import React from "react";
import "./ChatInput.css";

import attachIcon from "../assets/attachIcon.svg";
import sendIcon from "../assets/sendIcon.svg";

export default function ChatInput() {
  return (
    <div className="chat-input">
      <textarea
        placeholder="说出你的疑问"
        className="chat-input-textarea"
      ></textarea>

      <div className="chat-buttons">
        <button className="attach-btn">
          <img src={attachIcon} alt="添加附件" />
          <span>上传文件</span>
        </button>

        <button className="send-btn">
          <img src={sendIcon} alt="发送" />
          <span>发送</span>
        </button>
      </div>
    </div>
  );
}