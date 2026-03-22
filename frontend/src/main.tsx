import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css"; // global Tailwind + any shared styles

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
