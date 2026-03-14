import React from "react";
import ReactDOM from "react-dom/client";
import LivePreviewIDE from "./src/LivePreviewIDE";

function App() {
  return <LivePreviewIDE />;
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);