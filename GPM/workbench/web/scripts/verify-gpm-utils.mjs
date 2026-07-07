#!/usr/bin/env node
/** Magic-byte and filename helpers (mirrors gpmIngest.ts / gpmFilename.ts). */
const GPM_VERSIONS = new Set([4, 8, 9]);

function isGpmOrGpcMagic(head) {
  if (head.length < 4) return false;
  if (head[0] === 0x47 && head[1] === 0x50 && head[2] === 0x43 && head[3] === 0x01) return true;
  if (head[0] === 0x47 && head[1] === 0x50 && head[2] === 0x4d && GPM_VERSIONS.has(head[3])) return true;
  return false;
}

const UNSAFE_CHARS = /[/\\:*?"<>|\x00-\x1f]/g;
const SUFFIX_PATTERN = /\.(gpm|gpc)$/i;

function sanitizeExportBaseName(raw) {
  let name = raw.replace(UNSAFE_CHARS, "").trim();
  name = name.replace(SUFFIX_PATTERN, "").trim();
  return name || "document";
}

function normalizeGpmFilename(baseName, suffix = ".gpm") {
  return `${sanitizeExportBaseName(baseName)}${suffix}`;
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

assert(isGpmOrGpcMagic(new Uint8Array([0x47, 0x50, 0x4d, 0x09])), "GPM v9");
assert(isGpmOrGpcMagic(new Uint8Array([0x47, 0x50, 0x4d, 0x04])), "GPM v4");
assert(isGpmOrGpcMagic(new Uint8Array([0x47, 0x50, 0x43, 0x01])), "GPC");
assert(!isGpmOrGpcMagic(new Uint8Array([0x74, 0x65, 0x73, 0x74])), "plain text");
assert(sanitizeExportBaseName("mein/test.gpm") === "meintest", "sanitize path and suffix");
assert(normalizeGpmFilename("mein-test.gpm") === "mein-test.gpm", "no double suffix");
assert(normalizeGpmFilename("a/b:c") === "abc.gpm", "strip unsafe chars");

function formatSiPair(substance, permIndex) {
  return `S = ${String(substance)} · I = ${String(permIndex)}`;
}

assert(formatSiPair(372945, 13) === "S = 372945 · I = 13", "si pair");

console.log("verify-gpm-utils OK");
