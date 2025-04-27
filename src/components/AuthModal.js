import React, { useState } from "react";
import "./AuthModal.css";

// ✅【新增】引入封装好的接口
import { login, register, sendVerificationCode } from "../api/api"; // <-- 这里后期如果路径变了，需要改

export default function AuthModal({ isOpen, onClose }) {
  const [isRegister, setIsRegister] = useState(false); // 初始为登录界面
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    verificationCode: ""
  });
  const [isVerificationCodeSent, setIsVerificationCodeSent] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [errorMessage, setErrorMessage] = useState(""); // 用于显示错误消息

  // ✅【需要修改】处理表单提交，真正调用接口
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isRegister && formData.password !== formData.confirmPassword) {
      setErrorMessage("两次输入的密码不一致！");
      return;
    }

    try {
      if (isRegister) {
        // ✅【新增】真正调用 register 接口
        await register(formData.email, formData.password, formData.verificationCode);
        alert("注册成功！");
      } else {
        // ✅【新增】真正调用 login 接口
        const response = await login(formData.email, formData.password);
        if (response.data.access_token) {
          localStorage.setItem("token", response.data.access_token); // 登录后保存 token
        }
        alert("登录成功！");
      }
      onClose(); // 成功后关闭弹窗
    } catch (error) {
      console.error("请求失败：", error);
      setErrorMessage(error.response?.data?.error || "请求失败，请稍后再试");
    }
  };

  // ✅【需要修改】发送验证码，真正调用接口
  const sendCode = async () => {
    if (!formData.email) {
      alert("请输入邮箱");
      return;
    }

    setSendingCode(true);
    setErrorMessage(""); // 清空错误信息

    try {
      // ✅【新增】真正调用发送验证码接口
      await sendVerificationCode(formData.email);
      alert("验证码已发送，请查收邮箱");
      setIsVerificationCodeSent(true);
    } catch (error) {
      console.error("发送验证码失败：", error);
      setErrorMessage(error.response?.data?.error || "发送验证码失败，请稍后再试");
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
            <button onClick={onClose} className="close-btn">
              ×
            </button>
          </div>

          {errorMessage && <div className="error-message">{errorMessage}</div>} {/* 显示错误信息 */}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>{isRegister ? "注册邮箱" : "登录邮箱"}</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
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
                  onClick={sendCode} // ✅【这里改了】原来是 sendVerificationCode，改成调用新函数 sendCode
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
                    onChange={(e) =>
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
                    onChange={(e) =>
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
                    onChange={(e) =>
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
                  onChange={(e) =>
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
