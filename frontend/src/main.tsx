import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// The root div is defined in index.html and is always present, so this
// assertion is safe.
const rootElement = document.getElementById("root")!;

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
