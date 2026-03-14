/**
 * Builds a self-contained HTML document for Vue 3 code.
 * Handles both SFC format (<template>/<script>/<style>) and bare options objects.
 * Loads Vue 3 global build from unpkg.
 */
export function buildVueDoc(code) {
  const sfcBlock = code.includes('<template>') ? buildFromSFC(code) : buildFromOptions(code);

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>* { box-sizing: border-box; } body { margin: 0; font-family: system-ui, sans-serif; }</style>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body>
  <div id="app"></div>
  <script>
    try {
      const { createApp, defineComponent, ref, reactive, computed, onMounted, watch } = Vue;
      ${sfcBlock}
    } catch (e) {
      document.body.innerHTML = '<pre style="color:#ff6b6b;padding:1rem;font-size:13px;margin:0">' + e.message + '</pre>';
    }
  </script>
</body>
</html>`;
}

function buildFromSFC(code) {
  return `
      const __sfcCode = ${JSON.stringify(code)};
      const templateMatch = __sfcCode.match(/<template>([\\s\\S]*?)<\\/template>/);
      const scriptMatch   = __sfcCode.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/);
      const styleMatch    = __sfcCode.match(/<style[^>]*>([\\s\\S]*?)<\\/style>/);

      if (styleMatch) {
        const styleEl = document.createElement('style');
        styleEl.textContent = styleMatch[1];
        document.head.appendChild(styleEl);
      }

      const templateStr = templateMatch ? templateMatch[1].trim() : '<div></div>';
      let compOptions = { template: templateStr };

      if (scriptMatch) {
        try {
          const scriptContent = scriptMatch[1].replace(/export\\s+default\\s*/, 'compOptions = Object.assign(compOptions, ');
          eval(scriptContent + ')');
        } catch (e) {}
      }

      createApp(compOptions).mount('#app');
  `;
}

function buildFromOptions(code) {
  const optionsBody = code.includes('export default')
    ? code.replace(/export\s+default\s*/, '')
    : `{ setup() { ${code}; return {} }, template: '<div></div>' }`;

  return `
      const compOptions = ${optionsBody};
      createApp(compOptions).mount('#app');
  `;
}
