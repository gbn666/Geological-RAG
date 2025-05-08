// // src/components/ChangePasswordModal.js
// import React, { useState } from "react";
// import "./ChangePasswordModal.css";
// import { changePassword } from "../api/api";

// export default function ChangePasswordModal({ isOpen, onClose }) {
//   const [oldPwd, setOldPwd] = useState("");
//   const [newPwd, setNewPwd] = useState("");
//   const [confirmPwd, setConfirmPwd] = useState("");
//   const [errorMessage, setErrorMessage] = useState("");

//   if (!isOpen) return null;

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setErrorMessage("");

//     if (newPwd !== confirmPwd) {
//       setErrorMessage("两次输入的新密码不一致");
//       return;
//     }

//     try {
//       await changePassword(oldPwd, newPwd);
//       alert("密码修改成功，请重新登录");
//       onClose();
//       // 这里可以强制登出并刷新
//       localStorage.removeItem("access_token");
//       localStorage.removeItem("user_email");
//       window.location.reload();
//     } catch (error) {
//       setErrorMessage(
//         error.response?.data?.error || "修改失败，请稍后重试"
//       );
//     }
//   };

//   return (
//     <div className="auth-modal-overlay">
//       <div className="auth-modal">
//         <div className="auth-header">
//           <h3>修改密码</h3>
//           <button onClick={onClose} className="close-btn">
//             ×
//           </button>
//         </div>

//         {errorMessage && (
//           <div className="error-message">{errorMessage}</div>
//         )}

//         <form onSubmit={handleSubmit} className="auth-form">
//           <div className="form-group">
//             <label>当前密码</label>
//             <input
//               type="password"
//               value={oldPwd}
//               onChange={(e) => setOldPwd(e.target.value)}
//               required
//             />
//           </div>

//           <div className="form-group">
//             <label>新密码</label>
//             <input
//               type="password"
//               value={newPwd}
//               onChange={(e) => setNewPwd(e.target.value)}
//               required
//             />
//           </div>

//           <div className="form-group">
//             <label>确认新密码</label>
//             <input
//               type="password"
//               value={confirmPwd}
//               onChange={(e) => setConfirmPwd(e.target.value)}
//               required
//             />
//           </div>

//           <div className="button-group">
//             <button type="submit" className="submit-btn">
//               提交
//             </button>
//             <button
//               type="button"
//               className="submit-btn cancel-btn"
//               onClick={onClose}
//             >
//               取消
//             </button>
//           </div>
//         </form>
//       </div>
//     </div>
//   );
// }
// src/components/ChangePasswordModal.js
import React, { useState } from "react";
import "./ChangePasswordModal.css";
import { changePassword } from "../api/auth";

export default function ChangePasswordModal({ isOpen, onClose }) {
  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    // 本地输入校验
    if (newPwd !== confirmPwd) {
      setErrorMessage("两次输入的新密码不一致");
      return;
    }

    const payload = { currentPassword: oldPwd, newPassword: newPwd };
    // 调试：打印并弹窗显示 payload 和 token
    console.log("[DEBUG] Payload to send:", payload);
    console.log("[DEBUG] Token:", localStorage.getItem("access_token"));
    alert(`调试 Payload: ${JSON.stringify(payload)}`);

    try {
      await changePassword(oldPwd, newPwd);
      alert("密码修改成功，请重新登录");
      onClose();
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_email");
      window.location.reload();
    } catch (error) {
      // 调试：弹窗显示后端响应体
      console.error("修改密码失败详情：", error.response?.data);
      alert(`后端返回：${JSON.stringify(error.response?.data)}`);
      const respData = error.response?.data || {};
      let msg = respData.error || respData.msg || "修改失败，请稍后重试";
      if (error.response?.status === 401 || error.response?.status === 422) {
        msg = msg || "身份验证失败，请重新登录";
      }
      setErrorMessage(msg);
    }
  };

  return (
    <div className="auth-modal-overlay">
      <div className="auth-modal">
        <div className="auth-header">
          <h3>修改密码</h3>
          <button onClick={onClose} className="close-btn">
            ×
          </button>
        </div>

        {errorMessage && (
          <div className="error-message">{errorMessage}</div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="oldPwd">当前密码</label>
            <input
              id="oldPwd"
              type="password"
              title="当前密码"
              placeholder="请输入当前密码"
              value={oldPwd}
              onChange={(e) => setOldPwd(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPwd">新密码</label>
            <input
              id="newPwd"
              type="password"
              title="新密码"
              placeholder="请输入新密码"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPwd">确认新密码</label>
            <input
              id="confirmPwd"
              type="password"
              title="确认新密码"
              placeholder="请再次输入新密码"
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
              required
            />
          </div>

          <div className="button-group">
            <button type="submit" className="submit-btn">
              提交
            </button>
            <button
              type="button"
              className="submit-btn cancel-btn"
              onClick={onClose}
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
