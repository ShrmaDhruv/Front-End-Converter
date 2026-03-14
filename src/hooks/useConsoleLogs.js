/**
 * Listens for postMessage events from the sandboxed iframe preview
 * and collects them into a log array.
 * Returns [logs, clearLogs].
 */
import { useState, useEffect } from "react";

const VALID_TYPES = new Set(["log", "error", "warn", "info"]);
const MAX_LOGS = 200;

export function useConsoleLogs() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const handler = (e) => {
      if (!e.data || typeof e.data !== "object") return;
      const { type, message, args } = e.data;
      if (!VALID_TYPES.has(type)) return;

      const text = message || (args || []).join(" ");
      setLogs(prev => [...prev.slice(-(MAX_LOGS - 1)), { type, message: text }]);
    };

    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, []);

  const clearLogs = () => setLogs([]);

  return [logs, clearLogs];
}
