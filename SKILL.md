---
name: session-handoff
description: When the user explicitly says "交接并新开会话", "handoff and start a new chat", or invokes $session-handoff, save the current task's context, start a fresh Codex chat where supported, update project memory, and stop for the user's next instruction. Do not run for questions about this workflow.
---

# Session handoff

Run this workflow only when the user asks to **perform** a handoff. The request authorizes creation of the handoff files, a new chat, a project-memory update, and archival of the old chat after successful receipt. Follow narrower instructions in the user's request. This skill is message-triggered; do not create a scheduled task.

## 1. Identify the project and surface

Determine the current project's exact root, current working directory, and whether this chat runs in the Codex desktop app, CLI, or IDE extension. Record the current Git branch, worktree path, and whether there are uncommitted changes without modifying them. If no local project is identifiable, ask for its path before writing files or starting a chat.

Check the applicable AGENTS.md files. Do not assume that the current worktree is the project's main checkout. The receiver must work in the **same working directory** so it sees uncommitted files. If the available chat-creation tool cannot use that directory, do not silently start it elsewhere; use the supported route for this surface or report the limitation.

## 2. Write a private, evidence-bound handoff

Use <current-working-directory>/.codex-handoff/ unless the project has an established private handoff location. Create .codex-handoff/.gitignore with the two lines below before writing any private data. In a Git repository, verify with git check-ignore that the handoff and project-memory paths are ignored; if either is already tracked or cannot be ignored, stop and explain the privacy issue. Never stage, commit, or publish those files.

    *
    !.gitignore

Name the new document handoff-YYYYMMDD-HHMMSS-<short-id>.md, using the user's local time. Use an existing handoff from this task's **continuous handoff chain**, the current chat's visible history and compacted context, and any explicitly identified predecessor chat. Read older chat summaries with an available thread-reading tool when necessary. Such summaries may omit details: state what was actually accessible and mark gaps. Do not infer facts from missing history or merge unrelated chats merely because they belong to the same project.

Make the new document independently usable. Include:

- Project root and working directory; source chat ID if available; predecessor handoff path; history coverage.
- Original goal, latest user instructions, durable preferences, and permission boundaries.
- Decisions, superseded decisions, rejected approaches, completed work, and concrete evidence.
- Changed files, Git/worktree state, validation results, outputs, and important links or commands.
- Remaining work, blockers, uncertain facts, and the exact next instruction: receive this handoff, update project memory, then wait.

Separate verified facts from inference. Summarize rather than copy the whole transcript. Omit secrets and irrelevant personal data. Read the saved file back before creating a receiver. If this source chat already created a receiver for the same handoff, reuse it instead of creating another.

## 3. Prepare the receiver's first task

Compose a first prompt with the **absolute** working-directory, handoff, project-memory and receipt paths. Save the exact prompt as receiver-prompt-<short-id>.md in the private directory for CLI and IDE use. The receiver's task is only to:

1. Read applicable AGENTS.md, this handoff and any existing .codex-handoff/project-memory.md; inspect referenced files only as needed.
2. Update project memory with still-current goals, preferences, decisions, file locations, work state, open questions and handoff provenance. Preserve useful prior entries, label unverified claims and remove superseded claims. This is a project file, not a claim that Codex's background memory store updated immediately.
3. In the project root AGENTS.md, preserve existing instructions and add or update one short, idempotent instruction to read the project-memory path **if it exists** at the start of future project chats. Express the path relative to the project root: use .codex-handoff/project-memory.md when the working directory is the root, or include the working directory's relative subpath when it is nested. Include only the path, never private memory contents.
4. Read the saved memory back, then write a receipt file under .codex-handoff/ naming this handoff and memory path and stating "接收完成，等待用户指令". On failure, do not write a success receipt.
5. Report receipt briefly, end the turn and wait. Do not resume the handoff's remaining project work, create another chat, or send messages to other chats.

Use the same one-time receiver prompt on every surface. Do not use a fork that carries the old chat history into the new context.

## 4. Start a new chat on the available surface

- **Desktop app:** Use the app's project-list and create-thread tools to create a new local project chat with the receiver prompt as its first task. Resolve the project ID from the current path; do not invent one. Confirm the resulting chat runs in the exact original worktree/working directory. A fresh project chat that opens in another checkout does **not** satisfy this requirement. Use the app's wait/read tools to check completion. After verifying the receipt, archive the source chat and open the receiver chat. If tool routing cannot preserve the worktree, report the limitation and leave the source chat available.
- **CLI:** Use the bundled scripts/start-cli-receiver.py with the exact working directory, prompt file, handoff path and receipt path. It invokes a **new, persisted** codex exec chat; it does not resume or fork this chat. The script reports the new thread ID and checks its exit status and receipt. Once receipt is verified, archive the old CLI chat **only if its exact session ID is known**; otherwise leave it available and report that archival needs the ID. Show the new thread ID and codex resume <id> command. The receiver chat exists and has completed its first task, but an active CLI terminal may still need codex resume to display it interactively.
- **IDE extension:** Save the handoff and a receiver-prompt-<short-id>.md containing the exact first task. Present that file and ask the user to create a new IDE chat with its contents. There is currently no verified Skill-accessible IDE API to create and switch chats automatically. Do not claim the receiver has run, update project memory on its behalf, or archive the source chat before the user completes this step.

Do not launch a receiver when the old chat's source directory is unknown, the private files are unsafe to write, or the new chat would lose access to the original worktree. In any failed or uncertain state, preserve the handoff and source chat and give the user the concrete next action.

## 5. Verify and finish

The receipt must name the current handoff and the project memory must exist. Verify both on disk; a successful chat-creation response alone is insufficient. Record the receiver ID in the handoff when available. On retry, first inspect that ID and its receipt; wait if the receiver is active, or resume it if it failed and a resume route is available. Do not create a duplicate receiver while a previous attempt is unresolved. Never archive the source until receipt is verified. Keep all handoffs recoverable; do not delete earlier records. Report the actual surface-specific outcome without claiming unavailable automation.

When create_thread succeeds in the desktop app, attach ::created-thread{threadId="actual-ID"} in the final message using the actual returned ID.
