/**
 * Export the current React application to one offline HTML file.
 * Run from the repository root: node scripts/export-standalone.mjs
 * The downloaded HTML itself requires no Node.js, installation, or server.
 */
import { build } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { mkdtemp, readFile, readdir, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { Script } from 'node:vm';
import assert from 'node:assert/strict';

const temporary = await mkdtemp(join(tmpdir(), 'lpu-single-file-'));

try {
  // A dedicated library build does not depend on the hosted preview's HTML shell.
  // React and ReactDOM are bundled, not loaded from a CDN.
  await build({
    configFile: false,
    publicDir: false,
    plugins: [react(), tailwindcss()],
    define: { 'process.env.NODE_ENV': JSON.stringify('production') },
    build: {
      outDir: temporary,
      emptyOutDir: true,
      minify: false,
      sourcemap: false,
      target: 'es2020',
      cssCodeSplit: false,
      lib: {
        entry: resolve('src/main.tsx'),
        name: 'LpuLostAndFound',
        formats: ['iife'],
        fileName: () => 'application.js',
        cssFileName: 'application',
      },
    },
  });

  const files = await readdir(temporary);
  assert(files.includes('application.js'), 'Missing bundled application');
  const cssFiles = files.filter(file => file.endsWith('.css'));
  assert(cssFiles.length > 0, 'Missing compiled styles');
  const javascript = await readFile(join(temporary, 'application.js'), 'utf8');
  const styles = (await Promise.all(cssFiles.map(file => readFile(join(temporary, file), 'utf8'))))
    .join('\n')
    .replace(/@import\s+(?:url\([^)]*\)|["'][^"']*["'])\s*;/g, '')
    .replace(/(["'])DM Sans\1/g, 'Arial');

  // Fail rather than silently ship a file that needs a second local asset.
  assert(!/@import\b/.test(styles), 'Unexpected external stylesheet');
  assert(!/url\(\s*["']?(?!data:|#)/i.test(styles), 'Unexpected external CSS asset');
  assert(!/^\s*import\s/m.test(javascript), 'Unexpected unbundled JavaScript import');
  new Script(javascript, { filename: 'lpu-lost-found.html' });

  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="LPU Smart Lost and Found System: a standalone, offline university prototype.">
  <title>LPU Smart Lost and Found System</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%23102849'/%3E%3Ctext x='32' y='39' text-anchor='middle' font-family='Arial' font-size='20' fill='white'%3ELPU%3C/text%3E%3C/svg%3E">
  <!--
  LPU SMART LOST AND FOUND — SINGLE-FILE EDITION

  HOW TO RUN
  1. Save this file as lpu-lost-found.html.
  2. Open the file in VS Code to inspect or edit it.
  3. Double-click the file to run it in a modern browser.
     VS Code's optional Live Server extension also works.
  No npm install, external assets, internet connection, or build step is needed
  to run this downloaded file.

  FILE ORGANISATION
  - The STYLE section below contains all compiled CSS.
  - The SCRIPT section contains the bundled React runtime, followed by the app.
  - Search for "function App(" to find the main application.
  - Search for "initialItems" to change the sample belongings.
  - Search for "function CampusArt" to edit the campus illustration.
  JavaScript is compiled and unminified; JSX has been converted to JS calls.

  DEMO LIMITATIONS
  Role selection is a demo, not authentication. Use fictional details only.
  Reports and claims are browser-local and are not sent to LPU.
  Some browsers restrict localStorage for file:// pages; in that case data
  lasts only until the page closes. Live Server provides a stable local origin.
  Existing data from the hosted preview is not included in this download.
  System fonts are used to keep this file independent of external services.
  -->
  <style>
${styles.replace(/<\/style/gi, '<\\/style')}
  </style>
</head>
<body>
  <noscript>This prototype needs JavaScript. Enable JavaScript and reopen this file.</noscript>
  <div id="root"></div>
  <script>
${javascript.replace(/<\/script/gi, '<\\/script')}
  </script>
</body>
</html>
`;

  assert.equal((html.match(/^\s*<script>\s*$/gm) || []).length, 1);
  assert.equal((html.match(/<\/script>/g) || []).length, 1);
  assert(html.includes('function App('), 'Missing application implementation');
  assert(!/<script[^>]+\bsrc=/i.test(html), 'Unexpected external script');
  await mkdir('public', { recursive: true });
  await writeFile('public/lpu-lost-found.html', html, 'utf8');
  console.log(`Standalone export passed syntax and self-containment checks (${Math.ceil(Buffer.byteLength(html) / 1024)} KB).`);
  console.log('Download: /lpu-lost-found.html');
} finally {
  await rm(temporary, { recursive: true, force: true });
}
