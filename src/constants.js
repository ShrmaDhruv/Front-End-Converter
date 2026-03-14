export const FW_META = {
  html:    { label: "HTML",    color: "#e44d26", bg: "rgba(228,77,38,0.15)" },
  react:   { label: "React",   color: "#61dafb", bg: "rgba(97,218,251,0.12)" },
  vue:     { label: "Vue",     color: "#42b883", bg: "rgba(66,184,131,0.12)" },
  angular: { label: "Angular", color: "#dd0031", bg: "rgba(221,0,49,0.12)" },
};

export const SNIPPETS = {
  html: `<!DOCTYPE html>
<html>
<head>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 2rem; text-align: center; max-width: 360px; }
    h1 { color: #f8fafc; font-size: 1.5rem; margin: 0 0 0.5rem; }
    p { color: #94a3b8; font-size: 0.875rem; line-height: 1.6; margin: 0 0 1.5rem; }
    button { background: #3b82f6; color: #fff; border: none; padding: 0.6rem 1.5rem; border-radius: 6px; cursor: pointer; font-size: 0.875rem; }
    button:hover { background: #2563eb; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Hello, World 👋</h1>
    <p>Edit this code and see your changes live in the preview panel.</p>
    <button onclick="this.textContent = 'Clicked!'">Click me</button>
  </div>
</body>
</html>`,

  react: `function App() {
  const [count, setCount] = React.useState(0);
  const [color, setColor] = React.useState('#3b82f6');

  const colors = ['#3b82f6','#8b5cf6','#ec4899','#10b981','#f59e0b'];

  return (
    <div style={{
      minHeight: '100vh', background: '#0f172a', display: 'flex',
      alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui'
    }}>
      <div style={{
        background: '#1e293b', border: '1px solid #334155',
        borderRadius: 12, padding: '2rem', textAlign: 'center', minWidth: 300
      }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>⚛️</div>
        <h2 style={{ color: '#f8fafc', margin: '0 0 8px' }}>React Counter</h2>
        <p style={{ color: '#94a3b8', fontSize: 14, margin: '0 0 24px' }}>
          A simple interactive component
        </p>
        <div style={{
          fontSize: 56, fontWeight: 700, color, marginBottom: 24,
          transition: 'color 0.3s'
        }}>
          {count}
        </div>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginBottom: 16 }}>
          <button onClick={() => setCount(c => c - 1)} style={btnStyle}>−</button>
          <button onClick={() => setCount(0)} style={{...btnStyle, background:'#374151'}}>Reset</button>
          <button onClick={() => setCount(c => c + 1)} style={btnStyle}>+</button>
        </div>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
          {colors.map(c => (
            <div key={c} onClick={() => setColor(c)} style={{
              width: 20, height: 20, borderRadius: '50%', background: c,
              cursor: 'pointer', border: color === c ? '2px solid white' : '2px solid transparent'
            }}/>
          ))}
        </div>
      </div>
    </div>
  );
}

const btnStyle = {
  background: '#3b82f6', color: '#fff', border: 'none',
  padding: '8px 20px', borderRadius: 6, cursor: 'pointer', fontSize: 16
};`,

  vue: `<template>
  <div class="app">
    <div class="card">
      <div class="icon">💚</div>
      <h2>Vue 3 Counter</h2>
      <p>Reactive state with Composition API</p>
      <div class="count" :style="{ color: activeColor }">{{ count }}</div>
      <div class="controls">
        <button @click="count--">−</button>
        <button @click="count = 0" class="reset">Reset</button>
        <button @click="count++">+</button>
      </div>
      <div class="message">{{ message }}</div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return { count: 0 }
  },
  computed: {
    activeColor() {
      if (this.count > 0) return '#10b981';
      if (this.count < 0) return '#ef4444';
      return '#94a3b8';
    },
    message() {
      if (this.count > 5) return '🔥 Getting high!';
      if (this.count < -5) return '📉 Going negative...';
      return '👆 Click the buttons';
    }
  }
}
</script>

<style>
.app { min-height:100vh;background:#0f172a;display:flex;align-items:center;justify-content:center;font-family:system-ui }
.card { background:#1e293b;border:1px solid #334155;border-radius:12px;padding:2rem;text-align:center;min-width:300px }
.icon { font-size:3rem;margin-bottom:1rem }
h2 { color:#f8fafc;margin:0 0 8px }
p { color:#94a3b8;font-size:14px;margin:0 0 24px }
.count { font-size:56px;font-weight:700;margin-bottom:24px;transition:color .3s }
.controls { display:flex;gap:8px;justify-content:center;margin-bottom:16px }
button { background:#3b82f6;color:#fff;border:none;padding:8px 20px;border-radius:6px;cursor:pointer;font-size:16px }
.reset { background:#374151 }
.message { color:#64748b;font-size:13px }
</style>`,

  angular: `import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: \`
    <div class="app">
      <div class="card">
        <div class="icon">🔴</div>
        <h2>Angular Component</h2>
        <p>Counter with TypeScript</p>
        <div class="count">{{ count }}</div>
        <div class="controls">
          <button (click)="decrement()">−</button>
          <button (click)="reset()" class="reset">Reset</button>
          <button (click)="increment()">+</button>
        </div>
      </div>
    </div>
  \`,
  styles: [\`
    .app { min-height:100vh;background:#0f172a;display:flex;align-items:center;justify-content:center;font-family:system-ui }
    .card { background:#1e293b;border:1px solid #334155;border-radius:12px;padding:2rem;text-align:center }
    .icon { font-size:3rem;margin-bottom:1rem }
    h2 { color:#f8fafc;margin:0 0 8px }
    p { color:#94a3b8;font-size:14px;margin:0 0 24px }
    .count { font-size:56px;font-weight:700;color:#f97316;margin-bottom:24px }
    .controls { display:flex;gap:8px;justify-content:center }
    button { background:#3b82f6;color:#fff;border:none;padding:8px 20px;border-radius:6px;cursor:pointer;font-size:16px }
    .reset { background:#374151 }
  \`]
})
export class AppComponent {
  count = 0;
  increment() { this.count++; }
  decrement() { this.count--; }
  reset() { this.count = 0; }
}`,
};
