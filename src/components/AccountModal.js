// src/components/AccountModal0511.js
import React from "react";
import "./AccountModal.css";

export default function AccountModal({ isOpen, onClose, onEdit, onLogout }) {
  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay">
      <div className="auth-modal">
        <div className="auth-header">
          <h3>账户设置</h3>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="account-options">
          <button className="account-btn" onClick={onEdit}>修改密码</button>
          <button className="account-btn logout-btn" onClick={onLogout}>退出登录</button>
        </div>
      </div>
    </div>
  );
}
