// src/components/ChatInput.js0511
import React, { useState } from 'react';
import './ChatInput.css';
import attachIcon from '../assets/attachIcon.svg';
import sendIcon from '../assets/sendIcon.svg';

export default function ChatInput({ onSend }) {
  const [text, setText]       = useState('');
  const [file, setFile]       = useState(null);
  const [preview, setPreview] = useState(null);
  const [sending, setSending] = useState(false);
  const [canSend, setCanSend] = useState(false);

  const handleTextChange = e => {
    const v = e.target.value;
    setText(v);
    setCanSend(v.trim().length > 0 || Boolean(file));
  };

  const handleFileChange = e => {
    const sel = e.target.files[0];
    if (sel && ['image/jpeg','image/png'].includes(sel.type)) {
      setFile(sel);
      setPreview(URL.createObjectURL(sel));
      setCanSend(true);
    } else {
      alert('仅支持 JPG/PNG 格式');
    }
  };

  const handleRemoveImage = () => {
    if (sending) return;
    setFile(null);
    setPreview(null);
    setCanSend(text.trim().length > 0);
  };

  const handleSend = async () => {
    if (sending) return;
    setSending(true);
    try {
      await onSend(text, file);
      setText('');
      setFile(null);
      setPreview(null);
      setCanSend(false);
    } catch (err) {
      alert(err.message || '发送失败，请重试');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chat-input-container">
      {/* 恢复这一层，配合 ChatInput.css */}
      <div className="chat-input">
        <textarea
          className="chat-input-textarea"
          placeholder="说出你的疑问"
          value={text}
          onChange={handleTextChange}
          disabled={sending}
        />
        {preview && (
          <div className="preview-container">
            <img src={preview} alt="预览" className="preview-image" />
            <button
              type="button"
              className="remove-image-btn"
              onClick={handleRemoveImage}
              disabled={sending}
            >×</button>
          </div>
        )}
        <div className="chat-buttons">
          <label
            className={`attach-btn ${sending ? 'disabled' : ''}`}
          >
            <img src={attachIcon} alt="上传文件" />
            <span>上传文件</span>
            <input
              type="file"
              accept="image/png,image/jpeg"
              hidden
              onChange={handleFileChange}
              disabled={sending}
            />
          </label>
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!canSend || sending}
          >
            <img src={sendIcon} alt="发送" />
            <span>{sending ? '发送中…' : '发送'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
