/**
 * Claude Code hook entry point for bootcamp (AGENTS.md §1-§3). One process per event,
 * registered in .claude/settings.json and handed the event as JSON on stdin:
 *
 *   PreToolUse        hint lock, then the guard on owned files and the bypass file
 *   UserPromptSubmit  prompt log
 *   Stop              clear this session's hint lock
 *
 * The hint lock is a file because every hook runs as its own process. /hint's skill
 * creates it after a passing gate with `node .claude/hooks/main.ts lock <session-id>`;
 * recording the hint, or the end of the turn, removes it.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { BYPASS, allowedHintCommand, checkBash, checkWrite } from "./guard.ts";
import { logPrompt, shouldLog } from "./prompts.ts";

export const LOCK = ".agent/hint-lock";

const WRITE_TOOLS = new Set(["Write", "Edit", "MultiEdit", "NotebookEdit"]);

export interface HookInput {
  hook_event_name?: string;
  session_id?: string;
  cwd?: string;
  prompt?: string;
  tool_name?: string;
  tool_input?: { command?: string; file_path?: string; notebook_path?: string };
}

export function findRepoRoot(start: string): string {
  let dir = path.resolve(start);
  for (;;) {
    if (fs.existsSync(path.join(dir, "scripts", "meta.py"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return path.resolve(start);
    dir = parent;
  }
}

/** Start the hint lock for one session. */
export function lockHint(root: string, sessionId: string): void {
  fs.mkdirSync(path.join(root, ".agent"), { recursive: true });
  fs.writeFileSync(path.join(root, LOCK), sessionId + "\n");
}

/** True while this session is preparing a hint. Another session's leftover lock is ignored. */
export function hintLocked(root: string, sessionId: string): boolean {
  try {
    const owner = fs.readFileSync(path.join(root, LOCK), "utf8").trim();
    return owner === "" || owner === sessionId;
  } catch {
    return false;
  }
}

export function unlockHint(root: string): void {
  fs.rmSync(path.join(root, LOCK), { force: true });
}

function denial(tool: string, target: string, why: string): string {
  return (
    `Blocked ${tool} on ${target}: ${why}. Per AGENTS.md §1, agents never write an exercise's ` +
    "README.md, mine.*, brute.*, generate.*, shim.*, or tests/*cases* unless the user asks for that edit in " +
    `the same prompt. Do not work around this. If the user did ask, tell them to run \`! touch ${BYPASS}\` ` +
    "and remove it afterwards."
  );
}

/** Reason to deny a tool call, or null to let it through. */
export function preToolUse(root: string, input: HookInput): string | null {
  const tool = input.tool_name ?? "";
  const command = input.tool_input?.command ?? "";

  if (hintLocked(root, input.session_id ?? "")) {
    if (tool === "Bash" && allowedHintCommand(command)) {
      unlockHint(root);
      return null;
    }
    return (
      "A hint is being prepared: the only tool call allowed is recording the hint. Run exactly " +
      "`uv run scripts/meta.py record-hint [--level N] <<'EOF' ... EOF`, then reply with the hint. " +
      "Everything a hint may read is already in the prompt."
    );
  }

  if (tool === "Bash") {
    const why = checkBash(root, command);
    return why === null ? null : denial(tool, BYPASS, why);
  }
  if (WRITE_TOOLS.has(tool)) {
    const target = input.tool_input?.file_path ?? input.tool_input?.notebook_path ?? "";
    if (target === "") return null;
    const why = checkWrite(root, target, input.cwd ?? root);
    return why === null ? null : denial(tool, target, why);
  }
  return null;
}

/** Handle one hook event. Returns what to print on stdout, or null for nothing. */
export function handle(input: HookInput): string | null {
  const root = findRepoRoot(input.cwd ?? process.cwd());
  const session = input.session_id ?? "";
  switch (input.hook_event_name) {
    case "PreToolUse": {
      const reason = preToolUse(root, input);
      if (reason === null) return null;
      return JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: reason,
        },
      });
    }
    case "UserPromptSubmit":
      // Whatever a UserPromptSubmit hook prints is added to the context, so print nothing.
      if (shouldLog(input.prompt ?? "", "user")) logPrompt(root, session, input.prompt ?? "");
      return null;
    case "Stop":
      // Safety net: never leave the lock on after a turn ends.
      if (hintLocked(root, session)) unlockHint(root);
      return null;
    default:
      return null;
  }
}

function main(): void {
  if (process.argv[2] === "lock") {
    lockHint(findRepoRoot(process.cwd()), process.argv[3] ?? "");
    return;
  }
  const out = handle(JSON.parse(fs.readFileSync(0, "utf8")) as HookInput);
  if (out !== null) process.stdout.write(out + "\n");
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
