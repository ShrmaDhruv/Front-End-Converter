/**
 * Textarea-based code editor with Tab→2-space support.
 * Swap the textarea for <Editor> from @monaco-editor/react
 * using the same value/onChange/framework props.
 */
import { useRef } from "react";
import { FW_META } from "../constants";

export function CodeEditor({ value, onChange, framework }) {
  const taRef = useRef(null);
  const fw = FW_META[framework];

  const handleKeyDown = (e) => {
    if (e.key !== "Tab") return;
    e.preventDefault();
    const { selectionStart: s, selectionEnd: end } = e.target;
    const next = value.substring(0, s) + "  " + value.substring(end);
    onChange(next);
    requestAnimationFrame(() => {
      taRef.current.selectionStart = taRef.current.selectionEnd = s + 2;
    });
  };

  return (
    <textarea
      ref={taRef}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={handleKeyDown}
      spellCheck={false}
      autoComplete="off"
      style={{
        width: "100%",
        height: "100%",
        background: "transparent",
        color: "#e2e8f0",
        border: "none",
        outline: "none",
        resize: "none",
        padding: "16px",
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
        fontSize: "13px",
        lineHeight: "1.7",
        caretColor: fw.color,
        tabSize: 2,
        display: "block",
        boxSizing: "border-box",
      }}
    />
  );
}
