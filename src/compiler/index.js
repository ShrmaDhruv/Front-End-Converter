/**
 * Main compiler entry point.
 * compileToDoc(code, framework) → full HTML string ready for iframe srcdoc.
 * injectConsoleBridge(html) → patches console/onerror to postMessage to host.
 */
import { buildHtmlDoc }    from "./buildHtmlDoc";
import { buildReactDoc }   from "./buildReactDoc";
import { buildVueDoc }     from "./buildVueDoc";
import { buildAngularDoc } from "./buildAngularDoc";

export function compileToDoc(code, framework) {
  switch (framework) {
    case "react":   return buildReactDoc(code);
    case "vue":     return buildVueDoc(code);
    case "angular": return buildAngularDoc(code);
    default:        return buildHtmlDoc(code);
  }
}

export const CONSOLE_BRIDGE_SCRIPT = `
<script>
(function () {
  const send = (type) => (...args) => {
    const serialized = args.map(a => {
      try { return typeof a === 'object' ? JSON.stringify(a) : String(a); }
      catch (e) { return '[object]'; }
    });
    parent.postMessage({ type, args: serialized }, '*');
  };
  window.console = {
    log:   send('log'),
    error: send('error'),
    warn:  send('warn'),
    info:  send('info'),
  };
  window.onerror = (msg, src, line) => {
    parent.postMessage({ type: 'error', message: msg + (line ? ' (line ' + line + ')' : '') }, '*');
  };
  window.addEventListener('unhandledrejection', e => {
    parent.postMessage({ type: 'error', message: 'Unhandled rejection: ' + e.reason }, '*');
  });
})();
</script>`;

export function injectConsoleBridge(html) {
  if (!html) return html;
  if (html.includes("</head>")) return html.replace("</head>", CONSOLE_BRIDGE_SCRIPT + "</head>");
  return CONSOLE_BRIDGE_SCRIPT + html;
}
