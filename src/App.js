//APP.JS
import React from "react";
import Sidebar from "./components/Sidebar";
import MainArea from "./components/MainArea";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <MainArea />
    </div>
  );
}

export default App;