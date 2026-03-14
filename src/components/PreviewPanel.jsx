/**
 * Right panel: sandboxed iframe that renders the compiled HTML document.
 * sandbox="allow-scripts" only — no allow-same-origin — so the iframe
 * gets a null origin and cannot access the host app's DOM or storage.
 */
export function PreviewPanel({ srcdoc }) {
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "#0a0e1a", overflow: "hidden" }}>
      {/* Header */}
      <div style={{
        height: 36, display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 12px", borderBottom: "1px solid #0f1729", flexShrink: 0,
        background: "#060a12",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 7, height: 7, borderRadius: "50%", background: "#10b981",
            boxShadow: "0 0 6px #10b98180",
          }} />
          <span style={{ fontSize: 11, color: "#334155", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            Preview
          </span>
        </div>
        <span style={{ fontSize: 11, color: "#1e3a5f" }}>sandbox · allow-scripts</span>
      </div>

      {/* iframe */}
      <div style={{ flex: 1, overflow: "hidden" }}>
        {srcdoc ? (
          <iframe
            srcDoc={srcdoc}
            sandbox="allow-scripts"
            title="Live preview"
            style={{ width: "100%", height: "100%", border: "none", background: "#fff" }}
          />
        ) : (
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "center",
            height: "100%", color: "#1e293b", fontSize: 13, fontFamily: "monospace",
          }}>
            Waiting for input…
          </div>
        )}
      </div>
    </div>
  );
}
