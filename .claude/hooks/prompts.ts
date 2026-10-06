/**
 * Prompt logging for the bootcamp hooks.
 *
 * Appends {ts, session_id, prompt, exercise, status} as one JSON line to
 * <active exercise>/.meta/prompts.jsonl, or to .agent/prompts.jsonl when no
 * exercise is active (.agent/active). The prompt is logged verbatim.
 *
 * Keep this module free of side effects on import so `node --test` can
 * exercise it directly. main.ts calls it from `UserPromptSubmit`.
 */

import * as fs from "node:fs";
import * as path from "node:path";

/** Background-task results and extension-injected prompts are not my prompts. */
export function shouldLog(text: string, source: string): boolean {
  if (source === "extension") return false;
  return !text.trimStart().startsWith("<task-notification>");
}

function readStatus(metaFile: string): string | null {
  try {
    const m = /^status\s*=\s*"([^"]*)"/m.exec(fs.readFileSync(metaFile, "utf8"));
    return m ? m[1] : null;
  } catch {
    return null;
  }
}

function readActive(root: string): string {
  try {
    return fs.readFileSync(path.join(root, ".agent", "active"), "utf8").trim();
  } catch {
    return "";
  }
}

/** Append one prompt record. Never throws: a logging problem must not block a prompt. */
export function logPrompt(root: string, sessionId: string, prompt: string): void {
  try {
    let exercise = readActive(root);
    let status: string | null = null;
    let log = path.join(root, ".agent", "prompts.jsonl");
    if (exercise) {
      const meta = path.join(root, exercise, ".meta", "exercise.toml");
      if (fs.existsSync(meta)) {
        status = readStatus(meta);
        log = path.join(root, exercise, ".meta", "prompts.jsonl");
      } else {
        exercise = "";
      }
    }
    const record = {
      ts: new Date().toISOString(),
      session_id: sessionId,
      prompt,
      exercise: exercise || null,
      status,
    };
    fs.mkdirSync(path.dirname(log), { recursive: true });
    fs.appendFileSync(log, JSON.stringify(record) + "\n");
  } catch (err) {
    process.stderr.write(`log_prompt: ${String(err)}\n`);
  }
}
