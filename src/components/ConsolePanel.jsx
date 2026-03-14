/**
 * Displays postMessage logs captured from the sandboxed iframe.
 * Accepts logs array from useConsoleLogs and an onClear callback.
 */
import { useRef, useEffect } from "react";

const TYPE_STYLE = {
  log:   { color: "#e2e8f0" },
  error: { color: "#f87171" },
  warn:  { color: "#fbbf24" },
  info:  { color: "#60a5fa" },
};

const TYPE_ICON = {
  log:   "›",
  error: "✖",
  warn:  "⚠",
  info:  "ℹ",
};

export function ConsolePanel({ logs, onClear }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", fontFamily: "monospace" }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "6px 12px", borderBottom: "1px solid #0f1729", flexShrink: 0,
      }}>
        <span style={{ fontSize: 11, color: "#475569", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Console
        </span>
        <button
          onClick={onClear}
          style={{ background: "none", border: "none", color: "#475569", cursor: "pointer", fontSize: 11, padding: "2px 6px" }}
        >
          Clear
        </button>
      </div>

      <div style={{ flex: 1, overflow: "auto", padding: "8px 12px" }}>
        {logs.length === 0 ? (
          <div style={{ color: "#334155", fontSize: 12, fontStyle: "italic" }}>No output yet.</div>
        ) : (
          logs.map((entry, i) => (
            <div key={i} style={{ fontSize: 12, lineHeight: 1.6, marginBottom: 2, ...TYPE_STYLE[entry.type] }}>
              <span style={{ color: "#475569", marginRight: 8 }}>{TYPE_ICON[entry.type]}</span>
              {entry.message}
            </div>
          ))
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
