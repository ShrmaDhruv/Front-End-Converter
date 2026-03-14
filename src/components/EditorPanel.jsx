/**
 * Left panel: editor header (framework label, line count, Copy/Reset),
 * the CodeEditor textarea, and the collapsible ConsolePanel.
 */
import { useState } from "react";
import { CodeEditor }    from "./CodeEditor";
import { ConsolePanel }  from "./ConsolePanel";
import { FW_META }       from "../constants";

export function EditorPanel({
  code,
  onCodeChange,
  framework,
  onReset,
  logs,
  onClearLogs,
  consoleOpen,
  fullWidth,
}) {
  const [copyLabel, setCopyLabel] = useState("Copy");
  const fw = FW_META[framework];

  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopyLabel("Copied!");
      setTimeout(() => setCopyLabel("Copy"), 1500);
    });
  };

  return (
    <div style={{
      flex: fullWidth ? 1 : "0 0 50%",
      display: "flex", flexDirection: "column",
      borderRight: fullWidth ? "none" : "1px solid #0f1729",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        height: 36, display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 12px", borderBottom: "1px solid #0f1729", flexShrink: 0,
        background: "#060a12",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: fw.color, opacity: 0.8 }}>
            {fw.label}
          </span>
          <span style={{ fontSize: 11, color: "#1e293b" }}>•</span>
          <span style={{ fontSize: 11, color: "#334155", fontFamily: "monospace" }}>
            {code.split("\n").length} lines
          </span>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <button onClick={handleCopy} style={actionBtnStyle}>{copyLabel}</button>
          <button onClick={onReset}    style={actionBtnStyle}>Reset</button>
        </div>
      </div>

      {/* Editor area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <div style={{ flex: 1, overflow: "auto" }}>
          <CodeEditor value={code} onChange={onCodeChange} framework={framework} />
        </div>

        {consoleOpen && (
          <div style={{ height: 180, borderTop: "1px solid #0f1729", background: "#050810", flexShrink: 0 }}>
            <ConsolePanel logs={logs} onClear={onClearLogs} />
          </div>
        )}
      </div>
    </div>
  );
}

const actionBtnStyle = {
  padding: "2px 8px", borderRadius: 3, fontSize: 11, cursor: "pointer",
  background: "transparent", color: "#475569", border: "1px solid #1e293b",
};
