//MainArea.js
import React from "react";
import "./MainArea.css";
import HeaderIntro from "./HeaderIntro";
import ChatInput from "./ChatInput";

export default function MainArea() {
  return (
    <div className="main-area">
      <HeaderIntro />
      <ChatInput />
    </div>
  );
}