/**
 * Manages framework state with optional auto-detection.
 * When autoDetect is true, the framework is inferred from the code on every change.
 * Returns { framework, setFramework, autoDetect, setAutoDetect }.
 */
import { useState, useEffect } from "react";
import { detectFramework } from "../compiler/detectFramework";

export function useFrameworkDetection(code) {
  const [framework, setFramework]     = useState("react");
  const [autoDetect, setAutoDetect]   = useState(true);

  useEffect(() => {
    if (!autoDetect) return;
    const detected = detectFramework(code);
    setFramework(detected);
  }, [code, autoDetect]);

  return { framework, setFramework, autoDetect, setAutoDetect };
}
