#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webSrc = path.resolve(__dirname, "../src");
const uiTextDir = path.resolve(__dirname, "../../../ui-text/de");

function walk(dir, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      if (ent.name === "node_modules") continue;
      walk(p, out);
    } else if (ent.name.endsWith(".tsx")) out.push(p);
  }
  return out;
}

function collectUiKeys() {
  const keys = new Set();
  for (const f of fs.readdirSync(uiTextDir)) {
    if (!f.endsWith(".ts") || f === "index.ts" || f === "articles.ts") continue;
    const mod = f.replace(".ts", "");
    const text = fs.readFileSync(path.join(uiTextDir, f), "utf8");
    const stack = [mod];
    const lines = text.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const indent = line.match(/^(\s*)/)?.[1].length ?? 0;
      const depth = Math.max(0, Math.floor(indent / 2));

      const sameLine = line.match(/^\s*([a-zA-Z0-9_]+):\s*"([^"]*)"\s*,?\s*$/);
      if (sameLine) {
        stack.length = depth + 1;
        stack[depth] = sameLine[1];
        keys.add(stack.filter(Boolean).join("."));
        continue;
      }

      const keyOnly = line.match(/^\s*([a-zA-Z0-9_]+):\s*$/);
      if (keyOnly) {
        const next = lines[i + 1] ?? "";
        const nextVal = next.match(/^\s*"([^"]*)"\s*,?\s*$/);
        if (nextVal) {
          stack.length = depth + 1;
          stack[depth] = keyOnly[1];
          keys.add(stack.filter(Boolean).join("."));
        }
        continue;
      }

      if (/^\s*[a-zA-Z0-9_]+:\s*\{/.test(line)) {
        const keyOpen = line.match(/^\s*([a-zA-Z0-9_]+):/);
        if (keyOpen) {
          stack.length = depth + 1;
          stack[depth] = keyOpen[1];
        }
      }
    }
  }
  return keys;
}

function main() {
  const errors = [];
  const validKeys = collectUiKeys();

  for (const file of walk(webSrc)) {
    const rel = path.relative(webSrc, file).replace(/\\/g, "/");
    if (rel.startsWith("content/")) continue;
    const text = fs.readFileSync(file, "utf8");

    if (text.includes("<select")) {
      errors.push(`${rel}: forbidden <select>`);
    }
    if (/\bJSON\.stringify\s*\(/.test(text)) {
      errors.push(`${rel}: forbidden JSON.stringify in UI`);
    }
    if (/["']NL["']/.test(text) || />\s*NL\s*</.test(text)) {
      errors.push(`${rel}: forbidden NL label`);
    }

    for (const m of text.matchAll(/\bt\s*\(\s*["']([^"']+)["']/g)) {
      if (!validKeys.has(m[1])) {
        errors.push(`${rel}: unknown t() key "${m[1]}"`);
      }
    }
  }

  if (errors.length) {
    console.error("validate-ui-text FAILED:\n");
    errors.forEach((e) => console.error("  -", e));
    process.exit(1);
  }
  console.log(`validate-ui-text OK (${validKeys.size} keys)`);
}

main();
