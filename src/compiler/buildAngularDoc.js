/**
 * Returns a placeholder document for Angular code.
 * Angular's compiler is too large to run in-browser; a backend
 * endpoint (e.g. POST /compile/angular) is required for live preview.
 */
export function buildAngularDoc() {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { margin: 0; font-family: monospace; background: #080c14; color: #e2e8f0; }
    .wrap { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 2rem; }
    .card { text-align: center; max-width: 380px; }
    .icon { font-size: 2.5rem; margin-bottom: 1rem; }
    .title { color: #dd0031; font-size: 14px; font-weight: 600; margin-bottom: 0.5rem; }
    .desc { color: #64748b; font-size: 12px; line-height: 1.7; margin-bottom: 1.5rem; }
    .box { background: #0f0f1a; border: 1px solid #1e293b; border-radius: 4px; padding: 0.75rem 1rem; text-align: left; font-size: 11px; color: #475569; }
    .box .label { color: #f6c90e; margin-bottom: 0.4rem; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="icon">⚙️</div>
      <div class="title">Angular detected</div>
      <div class="desc">
        Angular's compiler is too large to run in-browser.<br>
        Connect your backend compiler endpoint to enable live preview.
      </div>
      <div class="box">
        <div class="label"># Recommended: FastAPI endpoint</div>
        <div>POST /compile/angular</div>
        <div style="margin-top:4px">{ "source": "..." } → { "html": "..." }</div>
      </div>
    </div>
  </div>
</body>
</html>`;
}
