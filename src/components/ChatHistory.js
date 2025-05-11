// src/components/ChatHistory.js0511
import React from 'react';
import './ChatHistory.css';

const ChatHistory = ({ messages = [] }) => {
  return (
    <div className="chat-history">
      {messages.map((msg, i) => (
        <div key={i} className={`chat-message ${msg.sender}-msg`}>
          {msg.type === "text" ? (
            <div className="message-text">{msg.content}</div>
          ) : (
            <img
              src={msg.content}
              className="message-image"
              alt="用户上传"
            />
          )}
        </div>
      ))}
    </div>
  );
};

export default ChatHistory;



