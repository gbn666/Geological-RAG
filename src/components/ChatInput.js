// src/components/ChatInput.js

import React from "react";
import "./ChatInput.css";

// 下面的图标路径请根据你实际的路径来替换
import attachIcon from "../assets/attachIcon.svg"; // <<< 需要替换：添加附件图标
import sendIcon from "../assets/sendIcon.svg";     // <<< 需要替换：发送图标

export default function ChatInput() {
  return (
    <div className="chat-input">
      {/* 问题输入框 */}
      <textarea
        placeholder="说出你的疑问"
        className="chat-input-textarea"
      ></textarea>

      {/* 上传文件按钮 */}
      <button className="attach-btn">
        <img src={attachIcon} alt="添加附件" />
        <span>上传文件</span>
      </button>

      {/* 发送按钮 */}
      <button className="send-btn">
        <img src={sendIcon} alt="发送" />
      </button>
    </div>
  );
}
