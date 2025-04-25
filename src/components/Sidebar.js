// src/components/Sidebar.js

import React from "react";
import "./Sidebar.css";

// 下面的图标路径请根据你实际的路径来替换
import openSidebarIcon from "../assets/openSidebar.svg"; // <<< 需要替换：打开侧边
import newChatIcon from "../assets/newChat.svg";         // <<< 需要替换：新对话
import userIcon from "../assets/userIcon.svg";           // <<< 需要替换：用户图标
import moreIcon from "../assets/moreIcon.svg";           // <<< 需要替换：更多图标

export default function Sidebar() {
  return (
    <div className="sidebar-container">
      {/* 顶部 - 标题 + 打开侧边栏按钮 */}
      <div className="sidebar-header">
        <img
          src={openSidebarIcon}
          alt="打开侧边栏"
          className="collapse-icon"
        />
        <span className="logo-text">RockID</span>
      </div>

      {/* 新对话按钮 */}
      <div className="new-chat-btn">
        <img src={newChatIcon} alt="新对话" className="icon" />
        <span>新对话</span>
      </div>

      {/* 历史记录（示例：可根据你需求自己扩展） */}
      <div className="history-label">历史记录</div>
      <div className="history-desc">登录即可解锁历史对话</div>

      {/* 底部 - 登录 + 更多 */}
      <div className="sidebar-footer">
        <div className="login-btn">
          <img src={userIcon} alt="用户" className="icon" />
          <span>登录</span>
          <img src={moreIcon} alt="更多" className="more-icon" />
        </div>
      </div>
    </div>
  );
}
