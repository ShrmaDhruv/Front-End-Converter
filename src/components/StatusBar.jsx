/**
 * Bottom status bar showing auto-detect state, active framework,
 * error count, and character count.
 */
import { FW_META } from "../constants";

export function StatusBar({ autoDetect, framework, errorCount, charCount }) {
  const fw = FW_META[framework];

  return (
    <div style={{
      height: 24, display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "0 12px", borderTop: "1px solid #0a1120", background: "#030508",
      flexShrink: 0,
    }}>
      <div style={{ display: "flex", gap: 16 }}>
        <span style={{ fontSize: 11, color: "#1e3a5f" }}>
          Auto-detect:{" "}
          <span style={{ color: autoDetect ? "#10b981" : "#ef4444" }}>
            {autoDetect ? "on" : "off"}
          </span>
        </span>
        <span style={{ fontSize: 11, color: "#1e3a5f" }}>
          Detected: <span style={{ color: fw.color }}>{fw.label}</span>
        </span>
      </div>

      <div style={{ display: "flex", gap: 16 }}>
        {errorCount > 0 && (
          <span style={{ fontSize: 11, color: "#f87171" }}>
            {errorCount} error{errorCount !== 1 ? "s" : ""}
          </span>
        )}
        <span style={{ fontSize: 11, color: "#1e3a5f" }}>
          {charCount.toLocaleString()} chars
        </span>
        <span style={{ fontSize: 11, color: "#1e3a5f" }}>
          LivePreview IDE · Tab=2sp
        </span>
      </div>
    </div>
  );
}
