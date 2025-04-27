// src/components/Sidebar.js
import React, { useState } from "react";
import "./Sidebar.css";
import closeSidebarIcon from "../assets/closeSidebar.svg";
import newChatIcon from "../assets/newChat.svg";
import userIcon from "../assets/userIcon.svg";
import moreIcon from "../assets/moreIcon.svg";
import AuthModal from "./AuthModal"; // 引入登录/注册模态框组件

export default function Sidebar() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false); // 控制模态框的显示与隐藏

  return (
    <div className="sidebar-container">
      {/* 顶部 - 标题 + 关闭侧边栏按钮 */}
      <div className="sidebar-header">
        <img src={closeSidebarIcon} alt="关闭侧边栏" className="collapse-icon" />
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
        <div className="login-btn" onClick={() => setIsAuthModalOpen(true)}> {/* 点击登录按钮打开模态框 */}
          <img src={userIcon} alt="用户" className="icon" />
          <span>登录</span>
          <img src={moreIcon} alt="更多" className="more-icon" />
        </div>
      </div>

      {/* 登录/注册模态框 */}
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </div>
  );
}