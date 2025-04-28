//C:\Users\10177\rock-app\src\components\AuthModal.js
import React, { useState } from "react";
import "./AuthModal.css";
import { login, register, sendVerificationCode } from "../api/api";

export default function AuthModal({ isOpen, onClose, onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    verificationCode: ""
  });
  const [isVerificationCodeSent, setIsVerificationCodeSent] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    if (isRegister && formData.password !== formData.confirmPassword) {
      setErrorMessage("两次输入的密码不一致！");
      return;
    }

    try {
      if (isRegister) {
        await register(
          formData.email,
          formData.password,
          formData.verificationCode
        );
        alert("注册成功！");
      } else {
        const { access_token } = await login(
          formData.email,
          formData.password
        );
        if (!access_token) {
          throw new Error("登录失败：未返回 access_token");
        }
        onLogin(formData.email);
        alert("登录成功！");
      }
      onClose();
    } catch (error) {
      console.error("请求失败：", error);
      setErrorMessage(
        error.response?.data?.error || error.message || "请求失败，请稍后再试"
      );
    }
  };

  const sendCode = async () => {
    if (!formData.email) {
      alert("请输入邮箱");
      return;
    }
    setSendingCode(true);
    setErrorMessage("");
    try {
      await sendVerificationCode(formData.email);
      alert("验证码已发送，请查收邮箱");
      setIsVerificationCodeSent(true);
    } catch (error) {
      console.error("发送验证码失败：", error);
      setErrorMessage(
        error.response?.data?.error || "发送验证码失败，请稍后再试"
      );
    } finally {
      setSendingCode(false);
    }
  };

  return (
    isOpen && (
      <div className="auth-modal-overlay">
        <div className="auth-modal">
          <div className="auth-header">
            <h3>{isRegister ? "注册" : "登录"}</h3>
            <button onClick={onClose} className="close-btn">×</button>
          </div>

          {errorMessage && <div className="error-message">{errorMessage}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>{isRegister ? "注册邮箱" : "登录邮箱"}</label>
              <input
                type="email"
                value={formData.email}
                onChange={e =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
              />
            </div>

            {isRegister && !isVerificationCodeSent && (
              <div className="form-group">
                <button
                  type="button"
                  className="verification-code-btn"
                  onClick={sendCode}
                  disabled={sendingCode}
                >
                  {sendingCode ? "发送中..." : "发送验证码"}
                </button>
              </div>
            )}

            {isRegister && isVerificationCodeSent && (
              <>
                <div className="form-group">
                  <label>验证码</label>
                  <input
                    type="text"
                    value={formData.verificationCode}
                    onChange={e =>
                      setFormData({ ...formData, verificationCode: e.target.value })
                    }
                    required
                  />
                </div>
                <div className="form-group">
                  <label>密码</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={e =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    required
                  />
                </div>
                <div className="form-group">
                  <label>确认密码</label>
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={e =>
                      setFormData({ ...formData, confirmPassword: e.target.value })
                    }
                    required
                  />
                </div>
              </>
            )}

            {!isRegister && (
              <div className="form-group">
                <label>密码</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={e =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  required
                />
              </div>
            )}

            <button type="submit" className="submit-btn">
              {isRegister ? "立即注册" : "登录"}
            </button>

            <div className="auth-toggle">
              {isRegister ? "已有账号？" : "没有账号？"}
              <button
                type="button"
                className="toggle-btn"
                onClick={() => setIsRegister(!isRegister)}
                disabled={isVerificationCodeSent}
              >
                {isRegister ? "登录" : "注册"}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  );
}