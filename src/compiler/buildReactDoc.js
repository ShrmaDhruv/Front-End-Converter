/**
 * Builds a self-contained HTML document for React/JSX code.
 * Loads React 18 and Babel standalone from unpkg, then mounts
 * the first recognized root component (App, Main, Component, Root, Page).
 */
export function buildReactDoc(code) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>* { box-sizing: border-box; } body { margin: 0; font-family: system-ui, sans-serif; }</style>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel" data-presets="react,env">
    try {
      ${code}
      const componentNames = ['App', 'Main', 'Component', 'Root', 'Page'];
      let RootComp = null;
      for (const name of componentNames) {
        try {
          if (typeof eval(name) === 'function') { RootComp = eval(name); break; }
        } catch (e) {}
      }
      if (!RootComp) throw new Error('No root component found. Export or define App, Main, Component, Root, or Page.');
      ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(RootComp));
    } catch (e) {
      document.body.innerHTML = '<pre style="color:#ff6b6b;padding:1rem;font-size:13px;margin:0">' + e.message + '</pre>';
    }
  </script>
</body>
</html>`;
}
