/**
 * Root component. Orchestrates state and wires all panels together.
 * All logic lives in hooks and sub-components — this file only connects them.
 */
import { useState } from "react";

import { SNIPPETS }                   from "./constants";
import { useCompiler }                from "./hooks/useCompiler";
import { useConsoleLogs }             from "./hooks/useConsoleLogs";
import { useFrameworkDetection }      from "./hooks/useFrameworkDetection";

import { TopBar }       from "./components/TopBar";
import { EditorPanel }  from "./components/EditorPanel";
import { PreviewPanel } from "./components/PreviewPanel";
import { StatusBar }    from "./components/StatusBar";

export default function LivePreviewIDE() {
  const [code, setCode]               = useState(SNIPPETS.react);
  const [panelLayout, setPanelLayout] = useState("split");
  const [consoleOpen, setConsoleOpen] = useState(false);

  const { framework, setFramework, autoDetect, setAutoDetect } = useFrameworkDetection(code);
  const srcdoc                                                  = useCompiler(code, framework);
  const [logs, clearLogs]                                       = useConsoleLogs();

  const handleFrameworkChange = (fw) => {
    setAutoDetect(false);
    setFramework(fw);
    setCode(SNIPPETS[fw]);
    clearLogs();
  };

  const handleReset = () => {
    setCode(SNIPPETS[framework]);
    clearLogs();
  };

  const errorCount = logs.filter(l => l.type === "error").length;

  return (
    <div style={{
      height: "100vh", display: "flex", flexDirection: "column",
      background: "#080c14", color: "#e2e8f0",
      fontFamily: "system-ui, -apple-system, sans-serif",
      overflow: "hidden",
    }}>
      <TopBar
        framework={framework}
        onFrameworkChange={handleFrameworkChange}
        autoDetect={autoDetect}
        onAutoDetectToggle={() => setAutoDetect(a => !a)}
        panelLayout={panelLayout}
        onLayoutChange={setPanelLayout}
        consoleOpen={consoleOpen}
        onConsoleToggle={() => setConsoleOpen(o => !o)}
        errorCount={errorCount}
      />

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {panelLayout !== "preview" && (
          <EditorPanel
            code={code}
            onCodeChange={setCode}
            framework={framework}
            onReset={handleReset}
            logs={logs}
            onClearLogs={clearLogs}
            consoleOpen={consoleOpen}
            fullWidth={panelLayout === "editor"}
          />
        )}

        {panelLayout !== "editor" && (
          <PreviewPanel srcdoc={srcdoc} />
        )}
      </div>

      <StatusBar
        autoDetect={autoDetect}
        framework={framework}
        errorCount={errorCount}
        charCount={code.length}
      />
    </div>
  );
}
