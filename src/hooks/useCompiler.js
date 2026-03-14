/**
 * Debounced compilation hook.
 * Watches code + framework, recompiles after 400ms of silence,
 * and returns the final srcdoc string with the console bridge injected.
 */
import { useState, useEffect, useRef } from "react";
import { compileToDoc, injectConsoleBridge } from "../compiler";

const DEBOUNCE_MS = 400;

export function useCompiler(code, framework) {
  const [srcdoc, setSrcdoc] = useState("");
  const timerRef = useRef(null);

  useEffect(() => {
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      const raw = compileToDoc(code, framework);
      setSrcdoc(injectConsoleBridge(raw));
    }, DEBOUNCE_MS);

    return () => clearTimeout(timerRef.current);
  }, [code, framework]);

  return srcdoc;
}
