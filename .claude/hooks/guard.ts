/**
 * Pure guard logic for the bootcamp hooks (AGENTS.md §1, §3).
 *
 * Owned, inside <lang>/exercises/<slug>/:
 *   README.md at the exercise root; mine.*, brute.*, generate.*, shim.* anywhere;
 *   files under tests/ whose path contains "cases".
 *
 * Keep this module free of side effects on import so `node --test` can
 * exercise it directly. main.ts wires these functions to `PreToolUse`.
 */

import * as fs from "node:fs";
import * as path from "node:path";

export const BYPASS = ".agent/allow-owned-edits";

const EXERCISE_RE = /^(python|rust|cpp)\/exercises\/([^/]+)\/(.+)$/;

const OWNED: Record<string, string> = {
  mine: "my solution",
  brute: "my brute-force oracle",
  generate: "my generator/adapter",
  shim: "my parse/format shim",
};

/** Why a path inside an exercise dir is owned, or null if agents may write it. */
export function ownedReason(inner: string): string | null {
  const parts = inner.split("/");
  if (parts[0] === ".meta" || parts[0] === "analysis") return null;
  if (inner === "README.md") return "README.md is my write-up of the problem";
  const name = parts[parts.length - 1];
  const stem = name.split(".")[0];
  if (stem in OWNED) return `${name} is ${OWNED[stem]}`;
  if (parts[0] === "tests" && parts.slice(1).join("/").includes("cases")) {
    return `${inner} holds my test cases`;
  }
  return null;
}

/** Repo-relative posix path, or null when the path is outside the repo. */
export function toRel(root: string, filePath: string, base: string = root): string | null {
  const abs = path.isAbsolute(filePath) ? filePath : path.join(base, filePath);
  const rel = path.relative(root, path.resolve(abs));
  if (rel === "" || rel.startsWith("..") || path.isAbsolute(rel)) return null;
  return rel.split(path.sep).join("/");
}

/** Best effort: shell commands that would create the bypass file. Mentioning it (grep, git commit -m) is fine. */
export function createsBypass(command: string): boolean {
  return /(\b(touch|cp|mv|ln|install|tee|truncate|dd)\b[^;&|\n]*|>\s*)\S*allow-owned-edits/.test(command);
}

/**
 * The hinter may only record the hint:
 *   uv run [<path>/]scripts/meta.py record-hint [--level N] <<'EOF'
 *   ...hint text...
 *   EOF
 * Anything else (reading files, other commands, chaining) is denied.
 */
export function allowedHintCommand(command: string): boolean {
  const lines = command.trim().split("\n");
  if (lines.length < 3) return false;
  const m = /^uv run (?:\S*\/)?scripts\/meta\.py record-hint(?: --level [1-3])? <<'(?<tag>[A-Z_]+)'$/.exec(
    lines[0].trim(),
  );
  return m !== null && lines[lines.length - 1].trim() === m.groups?.tag;
}

/** Reason to block a write/edit on an owned file, or null to allow it. `base` is the tool's cwd. */
export function checkWrite(root: string, filePath: string, base: string = root): string | null {
  const rel = toRel(root, filePath, base);
  if (rel === null) return null; // outside the project
  if (rel === BYPASS) return "only the user creates the bypass file";
  const m = EXERCISE_RE.exec(rel);
  if (m === null) return null;
  const why = ownedReason(m[3]);
  if (why !== null && !fs.existsSync(path.join(root, BYPASS))) return why;
  return null;
}

/** Reason to block a bash command, or null to allow it. */
export function checkBash(_root: string, command: string): string | null {
  if (createsBypass(command)) return "only the user creates the bypass file";
  return null;
}
