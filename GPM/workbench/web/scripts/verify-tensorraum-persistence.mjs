#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildSync } from "esbuild";

const dir = mkdtempSync(join(tmpdir(), "gpm-verify-tensorraum-"));
const outfile = join(dir, "run.mjs");

try {
  buildSync({
    entryPoints: ["scripts/verify-tensorraum-persistence.ts"],
    bundle: true,
    platform: "node",
    format: "esm",
    outfile,
    logLevel: "silent",
  });
  const result = spawnSync(process.execPath, [outfile], { stdio: "inherit" });
  process.exit(result.status ?? 1);
} finally {
  rmSync(dir, { recursive: true, force: true });
}
