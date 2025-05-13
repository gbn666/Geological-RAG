// // src/components/ChatHistory.js0511
// import React from 'react';
// import './ChatHistory.css';

// const ChatHistory = ({ messages = [] }) => {
//   return (
//     <div className="chat-history">
//       {messages.map((msg, i) => (
//         <div key={i} className={`chat-message ${msg.sender}-msg`}>
//           {msg.type === "text" ? (
//             <div className="message-text">{msg.content}</div>
//           ) : (
//             <img
//               src={msg.content}
//               className="message-image"
//               alt="用户上传"
//             />
//           )}
//         </div>
//       ))}
//     </div>
//   );
// };

// export default ChatHistory;



// File: components/ChatHistory.js
import React from 'react';
import './ChatHistory.css';
import ReactMarkdown from "react-markdown";

export default function ChatHistory({ messages }) {
  return (
    <div className="chat-history">
      {messages.map((msg, i) => (
        <div key={i} className={`chat-message ${msg.sender}-msg`}>
          {msg.type === 'text' ? (
            msg.sender === 'bot' ? (
              <div className="message-text bot-markdown">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            ) : (
              <div className="message-text">{msg.content}</div>
            )
          ) : (
            <img src={msg.content} className="message-image" alt="用户上传" />
          )}
        </div>
      ))}
    </div>
  );
}
