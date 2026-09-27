/**
 * Ports the log_prompt.py half of .claude/hooks/tests/test_hooks.py.
 * Run: node --test .pi/extensions/bootcamp/tests
 */

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { test } from "node:test";
import { logPrompt, shouldLog } from "../prompts.ts";

const EX = "python/exercises/lc0001-two-sum";

function makeProject(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "bootcamp-"));
  const meta = path.join(root, EX, ".meta");
  fs.mkdirSync(meta, { recursive: true });
  fs.writeFileSync(path.join(meta, "exercise.toml"), 'status = "attempting"\ntier = "quick"\n');
  fs.mkdirSync(path.join(root, ".agent"), { recursive: true });
  return root;
}

function records(file: string): any[] {
  return fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter((l) => l.length > 0)
    .map((l) => JSON.parse(l));
}

test("logs a prompt when no exercise is active", () => {
  const root = makeProject();
  logPrompt(root, "abc123", "Why does my stress test fail at n=0?");
  const [record] = records(path.join(root, ".agent", "prompts.jsonl"));
  assert.equal(record.session_id, "abc123");
  assert.equal(record.prompt, "Why does my stress test fail at n=0?");
  assert.equal(record.exercise, null);
  assert.equal(record.status, null);
  assert.equal(record.ts.slice(0, 2), "20");
});

test("logs to the active exercise", () => {
  const root = makeProject();
  fs.writeFileSync(path.join(root, ".agent", "active"), `${EX}\n`);
  logPrompt(root, "abc123", "first");
  logPrompt(root, "abc123", "second");
  const log = path.join(root, EX, ".meta", "prompts.jsonl");
  const all = records(log);
  assert.equal(all.length, 2);
  assert.equal(all[0].exercise, EX);
  assert.equal(all[0].status, "attempting");
  assert.equal(fs.existsSync(path.join(root, ".agent", "prompts.jsonl")), false);
});

test("background-task notifications and extension prompts are not logged", () => {
  assert.equal(shouldLog("<task-notification> done</task-notification>", "interactive"), false);
  assert.equal(shouldLog("hello", "extension"), false);
  assert.equal(shouldLog("hello", "interactive"), true);
  assert.equal(shouldLog("hello", "rpc"), true);
});
