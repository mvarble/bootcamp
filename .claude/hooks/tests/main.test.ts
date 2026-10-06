/**
 * The Claude Code adapter: hook event JSON in, a deny decision (or nothing) out.
 * Run: node --test ".claude/hooks/tests/*.test.ts"
 */

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { test } from "node:test";
import { LOCK, handle, hintLocked, lockHint, preToolUse } from "../main.ts";

const EX = "python/exercises/lc0001-two-sum";
const MINE = `${EX}/src/lc0001_two_sum/mine.py`;

const HINT_OK = `uv run scripts/meta.py record-hint --level 2 <<'EOF'
Try a running state.
EOF`;

function makeProject(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "bootcamp-"));
  const meta = path.join(root, EX, ".meta");
  fs.mkdirSync(meta, { recursive: true });
  fs.writeFileSync(path.join(meta, "exercise.toml"), 'status = "attempting"\ntier = "quick"\n');
  fs.mkdirSync(path.join(root, ".agent"), { recursive: true });
  fs.mkdirSync(path.join(root, "scripts"), { recursive: true });
  fs.writeFileSync(path.join(root, "scripts", "meta.py"), "");
  return root;
}

function decision(out: string | null): string | undefined {
  return out === null ? undefined : JSON.parse(out).hookSpecificOutput.permissionDecision;
}

for (const tool of ["Write", "Edit"]) {
  test(`${tool} on an owned file is denied`, () => {
    const root = makeProject();
    const input = { tool_name: tool, cwd: root, tool_input: { file_path: path.join(root, MINE) } };
    assert.match(preToolUse(root, input) ?? "", /mine\.py is my solution/);
  });
}

test("a write under analysis/ is allowed", () => {
  const root = makeProject();
  const input = { tool_name: "Write", cwd: root, tool_input: { file_path: path.join(root, EX, "analysis/review.md") } };
  assert.equal(preToolUse(root, input), null);
});

test("bash may not create the bypass file", () => {
  const root = makeProject();
  const input = { tool_name: "Bash", cwd: root, tool_input: { command: "touch .agent/allow-owned-edits" } };
  assert.ok(preToolUse(root, input));
  assert.equal(preToolUse(root, { ...input, tool_input: { command: "just check " + EX } }), null);
});

test("reads and other tools pass through", () => {
  const root = makeProject();
  assert.equal(preToolUse(root, { tool_name: "Read", cwd: root, tool_input: { file_path: path.join(root, MINE) } }), null);
});

test("handle prints a deny decision, from a subdirectory too", () => {
  const root = makeProject();
  const input = {
    hook_event_name: "PreToolUse",
    session_id: "s1",
    cwd: path.join(root, "python"),
    tool_name: "Edit",
    tool_input: { file_path: "exercises/lc0001-two-sum/src/lc0001_two_sum/mine.py" },
  };
  assert.equal(decision(handle(input)), "deny");
  assert.equal(handle({ ...input, tool_input: { file_path: "exercises/lc0001-two-sum/analysis/hints.md" } }), null);
});

test("the hint lock allows only recording the hint, then lifts", () => {
  const root = makeProject();
  lockHint(root, "s1");
  const base = { session_id: "s1", cwd: root };
  assert.match(preToolUse(root, { ...base, tool_name: "Read", tool_input: { file_path: "x" } }) ?? "", /hint is being prepared/);
  assert.ok(preToolUse(root, { ...base, tool_name: "Bash", tool_input: { command: "cat " + MINE } }));
  assert.equal(preToolUse(root, { ...base, tool_name: "Bash", tool_input: { command: HINT_OK } }), null);
  assert.equal(fs.existsSync(path.join(root, LOCK)), false);
  assert.equal(preToolUse(root, { ...base, tool_name: "Read", tool_input: { file_path: "x" } }), null);
});

test("another session's hint lock is ignored and left alone", () => {
  const root = makeProject();
  lockHint(root, "s1");
  assert.equal(hintLocked(root, "s2"), false);
  assert.equal(preToolUse(root, { session_id: "s2", cwd: root, tool_name: "Read", tool_input: { file_path: "x" } }), null);
  handle({ hook_event_name: "Stop", session_id: "s2", cwd: root });
  assert.equal(hintLocked(root, "s1"), true);
});

test("Stop clears this session's hint lock", () => {
  const root = makeProject();
  lockHint(root, "s1");
  assert.equal(handle({ hook_event_name: "Stop", session_id: "s1", cwd: root }), null);
  assert.equal(fs.existsSync(path.join(root, LOCK)), false);
});

test("UserPromptSubmit logs the prompt and prints nothing", () => {
  const root = makeProject();
  fs.writeFileSync(path.join(root, ".agent", "active"), EX + "\n");
  const out = handle({ hook_event_name: "UserPromptSubmit", session_id: "s1", cwd: root, prompt: "/hint" });
  assert.equal(out, null);
  const lines = fs.readFileSync(path.join(root, EX, ".meta", "prompts.jsonl"), "utf8").trim().split("\n");
  assert.deepEqual(JSON.parse(lines[0]).prompt, "/hint");
});
