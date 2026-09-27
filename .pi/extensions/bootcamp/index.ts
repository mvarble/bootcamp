/**
 * Bootcamp project extension for pi.
 *
 * Replaces the old Claude-Code hook bundle:
 *   - guard-owned  (was .claude/hooks/guard_owned.py): tool_call guard on owned files
 *   - log-prompt   (was .claude/hooks/log_prompt.py):   input handler that logs prompts
 *   - hint-lock    (was .claude/hooks/hint_scope.py):   in-process lock while a hint is prepared
 *   - commands     (were the .claude/skills/<name>/SKILL.md files): run the meta.py gate, then inject the task
 *
 * Loaded from .pi/extensions/ once the project is trusted. See AGENTS.md §1-§3.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import * as fs from "node:fs";
import * as path from "node:path";
import { BYPASS, allowedHintCommand, checkBash, checkWrite } from "./guard.ts";
import { renderTask, COMMAND_DESCRIPTIONS } from "./instructions.ts";
import { logPrompt, shouldLog } from "./prompts.ts";

const SKILLS = ["start", "hint", "done", "assess", "reference", "compare", "review", "due"];

/** Set by /hint, cleared when the hint is recorded (or the run settles). */
let hintLock = false;

function findRepoRoot(start: string): string {
  let dir = path.resolve(start);
  for (;;) {
    if (fs.existsSync(path.join(dir, "scripts", "meta.py"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return path.resolve(start);
    dir = parent;
  }
}

function deny(tool: string, target: string, why: string) {
  const reason =
    `Blocked ${tool} on ${target}: ${why}. Per AGENTS.md §1, agents never write an exercise's ` +
    "README.md, mine.*, brute.*, generate.*, shim.*, or tests/*cases* unless the user asks for that edit in " +
    `the same prompt. Do not work around this. If the user did ask, tell them to run \`! touch ${BYPASS}\` ` +
    "and remove it afterwards.";
  return { block: true, reason };
}

export default function bootcamp(pi: ExtensionAPI) {
  // --- Guards: owned files and the bypass file (was guard_owned.py) ----------

  pi.on("tool_call", async (event, ctx) => {
    const root = findRepoRoot(ctx.cwd);

    if (hintLock) {
      if (event.toolName === "bash" && allowedHintCommand(event.input.command as string)) {
        hintLock = false;
        return undefined;
      }
      return {
        block: true,
        reason:
          "A hint is being prepared: the only tool call allowed is recording the hint. Run exactly " +
          "`uv run scripts/meta.py record-hint [--level N] <<'EOF' ... EOF`, then reply with the hint. " +
          "Everything a hint may read is already in the prompt.",
      };
    }

    if (event.toolName === "bash") {
      const why = checkBash(root, event.input.command as string);
      return why === null ? undefined : deny("bash", BYPASS, why);
    }
    if (event.toolName === "write" || event.toolName === "edit") {
      const target = event.input.path as string;
      const why = checkWrite(root, target, ctx.cwd);
      return why === null ? undefined : deny(event.toolName, target, why);
    }
    return undefined;
  });

  // Safety net: never leave the lock on after a run settles.
  pi.on("agent_settled", async () => {
    hintLock = false;
  });

  // --- Prompt logging (was log_prompt.py) -----------------------------------

  pi.on("input", async (event, ctx) => {
    if (shouldLog(event.text ?? "", event.source)) {
      logPrompt(findRepoRoot(ctx.cwd), ctx.sessionManager.getSessionId(), event.text ?? "");
    }
    return { action: "continue" };
  });

  // --- Workflow commands (were skills; gate runs automatically) -------------

  for (const name of SKILLS) {
    pi.registerCommand(name, {
      description: COMMAND_DESCRIPTIONS[name],
      getArgumentCompletions:
        name === "start"
          ? (prefix: string) => {
              const langs = ["python", "rust", "cpp"].filter((l) => l.startsWith(prefix));
              return langs.length > 0 ? langs.map((value) => ({ value, label: value })) : null;
            }
          : undefined,
      handler: async (args: string, ctx: ExtensionContext) => {
        const root = findRepoRoot(ctx.cwd);
        const gate = await pi.exec("uv", ["run", "scripts/meta.py", "gate", name], { cwd: root, timeout: 30_000 });
        if (gate.code !== 0) {
          ctx.ui.notify((gate.stderr || gate.stdout).trim(), "error");
          return;
        }

        let extra = "";
        if (name === "due") {
          const due = await pi.exec("just", ["due"], { cwd: root, timeout: 60_000 });
          extra = `\n## Due list\n\n${(due.stdout || due.stderr).trim()}\n`;
        }

        const task = renderTask(name, args);
        const message =
          `## Gate\n\n${gate.stdout.trim()}\n${extra}\n` +
          `## Invocation\n\n\`${args.trim() || "(none)"}\`\n\n` +
          `## Task\n\n${task}\n`;

        if (name === "hint") hintLock = true;
        pi.sendUserMessage(message);
      },
    });
  }
}
