/**
 * The guard module: owned files, the bypass file, and the hint command.
 * Run: node --test ".claude/hooks/tests/*.test.ts"
 */

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { test } from "node:test";
import { BYPASS, allowedHintCommand, checkBash, checkWrite, ownedReason } from "../guard.ts";

const EX = "python/exercises/lc0001-two-sum";

function makeProject(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "bootcamp-"));
  const meta = path.join(root, EX, ".meta");
  fs.mkdirSync(meta, { recursive: true });
  fs.writeFileSync(path.join(meta, "exercise.toml"), 'status = "attempting"\ntier = "quick"\n');
  fs.mkdirSync(path.join(root, ".agent"), { recursive: true });
  return root;
}

const DENIED = [
  `${EX}/src/lc0001_two_sum/mine.py`,
  `${EX}/README.md`,
  `${EX}/tests/test_cases.py`,
  "rust/exercises/lc0001-two-sum/tests/cases/mod.rs",
  "cpp/exercises/lc0001-two-sum/generate.cpp",
  `${EX}/src/lc0001_two_sum/brute.py`,
  `${EX}/src/lc0001_two_sum/shim.py`,
];

const ALLOWED = [
  `${EX}/analysis/hints.md`,
  `${EX}/src/lc0001_two_sum/reference.py`,
  `${EX}/tests/conftest.py`,
  `${EX}/tests/test_samples.py`,
  "README.md",
  `${EX}/analysis/assessment.md`,
  "scripts/meta.py",
];

for (const rel of DENIED) {
  test(`guard denies owned file ${rel}`, () => {
    const root = makeProject();
    const why = checkWrite(root, rel);
    assert.ok(why, "expected a block reason");
  });
}

for (const rel of ALLOWED) {
  test(`guard allows other file ${rel}`, () => {
    const root = makeProject();
    assert.equal(checkWrite(root, rel), null);
  });
}

test("bypass file allows owned edits", () => {
  const root = makeProject();
  fs.writeFileSync(path.join(root, BYPASS), "");
  for (const rel of DENIED) {
    assert.equal(checkWrite(root, rel), null, rel);
  }
});

test("agents cannot create the bypass by writing it", () => {
  const root = makeProject();
  assert.ok(checkWrite(root, BYPASS));
});

test("agents cannot create the bypass from bash", () => {
  const root = makeProject();
  assert.ok(checkBash(root, "touch .agent/allow-owned-edits"));
  assert.ok(checkBash(root, "echo x > .agent/allow-owned-edits"));
  assert.ok(checkBash(root, "cp /tmp/x .agent/allow-owned-edits"));
});

test("mentioning the bypass is fine", () => {
  const root = makeProject();
  assert.equal(checkBash(root, "rm .agent/allow-owned-edits"), null);
  assert.equal(checkBash(root, "git commit -m 'allow-owned-edits'"), null);
  assert.equal(checkBash(root, `grep allow-owned-edits ${BYPASS}`), null);
});

test("ownedReason is scoped to the exercise", () => {
  assert.equal(ownedReason(".meta/exercise.toml"), null);
  assert.equal(ownedReason("analysis/hints.md"), null);
  assert.ok(ownedReason("mine.py"));
});

test("relative paths resolve against the tool cwd", () => {
  const root = makeProject();
  const cwd = path.join(root, "python");
  assert.ok(checkWrite(root, "exercises/lc0001-two-sum/src/lc0001_two_sum/mine.py", cwd));
  assert.equal(checkWrite(root, "exercises/lc0001-two-sum/analysis/hints.md", cwd), null);
});

const HINT_OK = `uv run scripts/meta.py record-hint --level 2 <<'EOF'
Try a running state.
EOF`;

test("hinter may record a hint", () => {
  assert.ok(allowedHintCommand(HINT_OK));
  assert.ok(allowedHintCommand("uv run /repo/scripts/meta.py record-hint <<'EOF'\nx\nEOF"));
});

for (const [name, command] of [
  ["reading a file", "cat analysis/reference.py"],
  ["chaining", `${HINT_OK}\nrm -rf /`],
  ["other meta command", "uv run scripts/meta.py show"],
] as const) {
  test(`hinter may do nothing else (${name})`, () => {
    assert.equal(allowedHintCommand(command), false);
  });
}
