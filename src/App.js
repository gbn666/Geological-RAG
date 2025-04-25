// src/App.js

import React from "react";
import Sidebar from "./components/Sidebar";
import MainArea from "./components/MainArea";
import "./App.css"; // 这里放一些全局样式

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <MainArea />
    </div>
  );
}

export default App;
