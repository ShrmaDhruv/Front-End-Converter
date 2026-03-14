/**
 * Wraps bare HTML fragments in a full document shell.
 * If the source already contains a doctype or html tag, returns it unchanged.
 */
export function buildHtmlDoc(code) {
  if (/<!DOCTYPE/i.test(code) || /<html/i.test(code)) return code;

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; padding: 1rem; }
  </style>
</head>
<body>
  ${code}
</body>
</html>`;
}
