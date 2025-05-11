// src/components/Sidebar.js0511
import React, { useState, useEffect } from "react";
import "./Sidebar.css";
import closeSidebarIcon from "../assets/closeSidebar.svg";
import newChatIcon from "../assets/newChat.svg";
import userIcon from "../assets/userIcon.svg";
import moreIcon from "../assets/moreIcon.svg";
import AuthModal from "./AuthModal";
import AccountModal from "./AccountModal";
import ChangePasswordModal from "./ChangePasswordModal";
import { getCurrentUser, logout as apiLogout } from "../api/auth";

export default function Sidebar() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);
  const [isChangePwdOpen, setIsChangePwdOpen] = useState(false);
  const [userEmail, setUserEmail] = useState("");

  // 初始化：看 localStorage 或调用 /me 接口
  useEffect(() => {
    const email = localStorage.getItem("user_email");
    if (email) {
      setUserEmail(email);
    } else if (localStorage.getItem("access_token")) {
      getCurrentUser()
        .then(user => {
          setUserEmail(user.email);
          localStorage.setItem("user_email", user.email);
        })
        .catch(() => setUserEmail(""));
    }
  }, []);

  // 登录成功回调
  const handleLoginSuccess = (email) => {
    setUserEmail(email);
    localStorage.setItem("user_email", email);
  };

  // 退出登录逻辑（带浏览器二次确认）
  const handleLogout = () => {
    if (window.confirm("确认要退出登录吗？")) {
      apiLogout();
      localStorage.removeItem("user_email");
      setUserEmail("");
      setIsAccountModalOpen(false);
    }
  };

  return (
    <div className="sidebar-container">
      {/* 顶部：Logo + 关闭按钮 */}
      <div className="sidebar-header">
        <img src={closeSidebarIcon} alt="关闭侧边栏" className="collapse-icon" />
        <span className="logo-text">RockID</span>
      </div>

      {/* 新对话按钮 */}
      <div className="new-chat-btn">
        <img src={newChatIcon} alt="新对话" className="icon" />
        <span>新对话</span>
      </div>

      {/* 历史记录提示 */}
      <div className="history-label">历史记录</div>
      <div className="history-desc">
        {userEmail ? "查看你的历史对话" : "登录即可解锁历史对话"}
      </div>

      {/* 底部：登录或用户名 */}
      <div className="sidebar-footer">
        <div
          className="login-btn"
          onClick={() =>
            userEmail
              ? setIsAccountModalOpen(true)
              : setIsAuthModalOpen(true)
          }
        >
          <img src={userIcon} alt="用户" className="icon" />
          {/* 只显示邮箱 @ 前的部分 */}
          <span>{userEmail ? userEmail.split("@")[0] : "登录"}</span>
          <img src={moreIcon} alt="更多" className="more-icon" />
        </div>
      </div>

      {/* 登录/注册 模态框 */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLogin={handleLoginSuccess}
      />

      {/* 账户设置 模态框（修改密码 / 退出登录） */}
      <AccountModal
        isOpen={isAccountModalOpen}
        onClose={() => setIsAccountModalOpen(false)}
        onEdit={() => {
          // 打开修改密码框，并关闭账户设置框
          setIsChangePwdOpen(true);
          setIsAccountModalOpen(false);
        }}
        onLogout={handleLogout}
      />

      {/* 修改密码 模态框 */}
      <ChangePasswordModal
        isOpen={isChangePwdOpen}
        onClose={() => setIsChangePwdOpen(false)}
      />
    </div>
  );
}



