/**
 * Detects the frontend framework from source code using pattern matching.
 * Returns one of: "html" | "react" | "vue" | "angular"
 */
export function detectFramework(code) {
  if (!code.trim()) return "html";

  if (/<template[\s>]/.test(code) && /<script/.test(code)) return "vue";

  if (/@Component\s*\(|@NgModule\s*\(|platformBrowserDynamic/.test(code)) return "angular";

  if (
    /import\s+React|from\s+['"]react['"]|jsx|\.tsx?/.test(code) ||
    (/const\s+\w+\s*=\s*\(\s*\)\s*=>/.test(code) && /<[A-Z]/.test(code))
  ) return "react";

  if (/<[a-z][^>]*>/.test(code) || /<!DOCTYPE/i.test(code)) return "html";

  if (/export\s+default\s*\{/.test(code) || /setup\s*\(/.test(code)) return "vue";

  return "html";
}
