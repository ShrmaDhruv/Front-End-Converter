/**
 * Top navigation bar with logo, framework switcher, auto-detect toggle,
 * layout controls, and console toggle button.
 */
import { FW_META } from "../constants";

const LAYOUT_OPTIONS = [
  ["split",   "▥", "Split"],
  ["editor",  "▤", "Editor only"],
  ["preview", "▦", "Preview only"],
];

export function TopBar({
  framework,
  onFrameworkChange,
  autoDetect,
  onAutoDetectToggle,
  panelLayout,
  onLayoutChange,
  consoleOpen,
  onConsoleToggle,
  errorCount,
}) {
  const fw = FW_META[framework];

  return (
    <div style={{
      height: 48, display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "0 16px", borderBottom: "1px solid #0f1729", flexShrink: 0,
      background: "#050810",
    }}>
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 22, height: 22, borderRadius: 4,
          background: "linear-gradient(135deg,#3b82f6,#8b5cf6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 12, fontWeight: 700, color: "#fff",
        }}>
          ▶
        </div>
        <span style={{ fontSize: 14, fontWeight: 600, letterSpacing: "-0.02em", color: "#f8fafc" }}>
          LivePreview
        </span>
        <span style={{ fontSize: 11, color: "#334155", marginLeft: 2 }}>IDE</span>
      </div>

      {/* Framework tabs */}
      <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
        {Object.entries(FW_META).map(([key, meta]) => (
          <button
            key={key}
            onClick={() => onFrameworkChange(key)}
            style={{
              padding: "4px 12px", borderRadius: 4, fontSize: 12, fontWeight: 500,
              cursor: "pointer", transition: "all 0.15s",
              background: framework === key ? meta.bg : "transparent",
              color: framework === key ? meta.color : "#475569",
              border: framework === key ? `1px solid ${meta.color}40` : "1px solid transparent",
            }}
          >
            {meta.label}
          </button>
        ))}

        {/* Auto-detect pill */}
        <div
          onClick={onAutoDetectToggle}
          style={{
            marginLeft: 8, padding: "4px 10px", borderRadius: 4, cursor: "pointer",
            background: "#0f1729", border: "1px solid #1e2d45",
            fontSize: 11, color: "#475569", display: "flex", gap: 6, alignItems: "center",
            userSelect: "none",
          }}
        >
          <span style={{
            width: 6, height: 6, borderRadius: "50%", display: "inline-block",
            background: autoDetect ? "#10b981" : "#475569",
          }} />
          Auto-detect
        </div>
      </div>

      {/* Layout + console controls */}
      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
        {LAYOUT_OPTIONS.map(([id, icon, title]) => (
          <button
            key={id}
            onClick={() => onLayoutChange(id)}
            title={title}
            style={{
              padding: "4px 8px", borderRadius: 4, fontSize: 14, cursor: "pointer",
              background: panelLayout === id ? "#1e293b" : "transparent",
              color: panelLayout === id ? "#94a3b8" : "#334155",
              border: "1px solid " + (panelLayout === id ? "#334155" : "transparent"),
            }}
          >
            {icon}
          </button>
        ))}

        <button
          onClick={onConsoleToggle}
          style={{
            padding: "4px 10px", borderRadius: 4, fontSize: 11, cursor: "pointer", marginLeft: 4,
            background: consoleOpen ? "#1e293b" : "transparent",
            color: consoleOpen ? "#94a3b8" : "#334155",
            border: "1px solid " + (consoleOpen ? "#334155" : "transparent"),
          }}
        >
          Console{" "}
          {errorCount > 0 && (
            <span style={{ color: "#f87171" }}>({errorCount})</span>
          )}
        </button>
      </div>
    </div>
  );
}
