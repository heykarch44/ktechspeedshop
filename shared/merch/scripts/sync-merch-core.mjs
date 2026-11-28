#!/usr/bin/env node
/**
 * Copy shared merch client assets into the host repo's public/js/
 * and write shared/merch/CHECKSUM (sha256 over VERSION + client/ + server/, LF-normalised).
 *
 * Usage:
 *   node shared/merch/scripts/sync-merch-core.mjs
 *   node shared/merch/scripts/sync-merch-core.mjs --check
 */
import { createHash } from "node:crypto";
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MERCH_ROOT = path.resolve(__dirname, "..");
const REPO_ROOT = path.resolve(MERCH_ROOT, "..", "..");
const PUBLIC_JS = path.join(REPO_ROOT, "public", "js");
const CHECKSUM_PATH = path.join(MERCH_ROOT, "CHECKSUM");

const CLIENT_FILES = [
  { src: path.join(MERCH_ROOT, "client", "merch-core.js"), dest: path.join(PUBLIC_JS, "merch-core.js") },
  { src: path.join(MERCH_ROOT, "client", "merch-core.css"), dest: path.join(PUBLIC_JS, "merch-core.css") },
];

async function listFilesRecursive(dir, base = dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const out = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...(await listFilesRecursive(full, base)));
    } else if (entry.isFile()) {
      out.push(path.relative(base, full).split(path.sep).join("/"));
    }
  }
  return out;
}

async function computeChecksum() {
  const hash = createHash("sha256");
  const version = await fs.readFile(path.join(MERCH_ROOT, "VERSION"), "utf8");
  hash.update(version.replace(/\r\n/g, "\n"));
  hash.update("\n");

  const clientFiles = (await listFilesRecursive(path.join(MERCH_ROOT, "client"))).sort();
  const serverFiles = (await listFilesRecursive(path.join(MERCH_ROOT, "server"))).sort();
  const relative = [
    ...clientFiles.map((f) => `client/${f}`),
    ...serverFiles.map((f) => `server/${f}`),
  ].sort();

  for (const rel of relative) {
    const raw = await fs.readFile(path.join(MERCH_ROOT, rel));
    const text = raw.toString("utf8").replace(/\r\n/g, "\n");
    hash.update(rel);
    hash.update("\n");
    hash.update(text);
    if (!text.endsWith("\n")) hash.update("\n");
  }

  return hash.digest("hex");
}

async function readIfExists(filePath) {
  try {
    return await fs.readFile(filePath);
  } catch (err) {
    if (err && err.code === "ENOENT") return null;
    throw err;
  }
}

async function main() {
  const checkOnly = process.argv.includes("--check");
  const expected = await computeChecksum();
  const checksumContents = `${expected}\n`;

  let stale = false;
  const reasons = [];

  const existingChecksum = await readIfExists(CHECKSUM_PATH);
  if (!existingChecksum || existingChecksum.toString("utf8").replace(/\r\n/g, "\n") !== checksumContents) {
    stale = true;
    reasons.push("CHECKSUM");
  }

  for (const { src, dest } of CLIENT_FILES) {
    const srcBuf = await fs.readFile(src);
    const destBuf = await readIfExists(dest);
    if (!destBuf || !srcBuf.equals(destBuf)) {
      stale = true;
      reasons.push(path.relative(REPO_ROOT, dest).split(path.sep).join("/"));
    }
  }

  if (checkOnly) {
    if (stale) {
      console.error(`[sync-merch-core] stale: ${reasons.join(", ")}`);
      process.exit(1);
    }
    console.log(`[sync-merch-core] ok ${expected}`);
    return;
  }

  await fs.mkdir(PUBLIC_JS, { recursive: true });
  for (const { src, dest } of CLIENT_FILES) {
    await fs.copyFile(src, dest);
  }
  await fs.writeFile(CHECKSUM_PATH, checksumContents, "utf8");
  console.log(`[sync-merch-core] wrote public/js copies + CHECKSUM ${expected}`);
}

main().catch((err) => {
  console.error("[sync-merch-core] failed", err);
  process.exit(1);
});
