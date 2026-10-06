# Threadlift for Codex

[Simplified Chinese](README.zh-CN.md) · English

**Pass the work. Start fresh.**

A user-level Codex skill for moving a long-running task into a fresh chat. Say **"handoff and start a new chat"** or invoke **$session-handoff**. The skill writes a concise handoff, starts a receiver where the current Codex surface supports it, updates a private project-memory file, and leaves the receiver waiting for your next instruction.

## What happens

1. The current chat summarizes its task and the continuous chain of earlier handoffs. It records decisions, completed work, files, validation, open questions, and gaps in accessible history.
2. Private records go under the current working directory's .codex-handoff/ folder. A local .gitignore protects those records from ordinary Git staging. The skill verifies that the files are ignored before writing them in a Git repository.
3. The receiving chat reads the handoff, updates .codex-handoff/project-memory.md, adds a short path-only pointer to the project's AGENTS.md, writes a receipt, and stops.
4. The old chat is archived only after the receipt is verified and only where the surface can identify and archive that exact chat.

This workflow starts when you request it. Closing a chat or approaching a context limit does not trigger it automatically.

## Surface support

| Surface | New receiver | What you do afterward |
| --- | --- | --- |
| Codex desktop app | Creates a fresh project chat and verifies its receipt when the app can keep the exact working directory | Continue in the opened receiver chat |
| Codex CLI | Starts a new persisted non-interactive Codex chat in the same directory and verifies its receipt | Use the printed session ID with codex resume to open it interactively |
| Codex IDE extension | Saves the handoff and an exact receiver prompt | Open a new IDE chat and paste the saved prompt |

The IDE extension has no verified skill-accessible API for creating and switching chats. The desktop flow stops rather than moving a worktree task into another checkout. The CLI can create the receiver automatically, while the current terminal may still need a resume command to show it.

## Install once for your user

If you have the packaged archive, extract `codex-threadlift.zip` and copy the entire `session-handoff/` folder into your user-level skills directory. **Do not copy only SKILL.md**; the CLI route also needs `scripts/`.

The `~/.codex/skills/session-handoff/` location has been tested with this version. On macOS/Linux, from the directory containing the extracted `session-handoff/` folder:

    mkdir -p ~/.codex/skills
    cp -R session-handoff ~/.codex/skills/

If that destination already exists, compare versions and merge or replace it before copying; repeating the command can create a nested folder. Other Codex installations may use `~/.agents/skills/session-handoff/` as the user-level location. Check the [official skill guide](https://learn.chatgpt.com/docs/build-skills) and your local skill list. Start a new Codex chat after installation; restart Codex if the skill does not appear.

You can instead clone this repository into your user-level skill directory:

    git clone https://github.com/EricZihaoHe/codex-threadlift.git ~/.codex/skills/session-handoff

Codex discovers user-level skills for future chats across your local projects. The skill's invocation name remains `session-handoff`.

After installation, in a local project chat:

    $session-handoff handoff and start a new chat

The plain phrase also matches the skill description, but explicitly invoking it is the most reliable trigger. A local project must be identifiable. The receiver never starts pending project tasks on its own.

## Privacy and project files

The skill package contains generic instructions and one CLI helper. **Do not add real handoff documents, project memory, chat transcripts, credentials, or personal project files to this repository.** The runtime .codex-handoff/ directory is created inside your own project and ignored by Git by default. A forced Git add or an existing tracked path can override ignore behavior, so inspect changes before publishing any project.

The project-memory file is immediately readable by the receiver. It is distinct from Codex's background-generated personal memory, which may update later. AGENTS.md contains only an instruction to read the private file if it exists; the memory contents stay out of AGENTS.md.

## Requirements and limits

- Codex with user-level skills enabled.
- Python 3.9+ and the codex CLI executable for the CLI route.
- A writable local project directory for the handoff and receipt.
- The Codex desktop app's project and chat tools for the desktop route.

The skill cannot reconstruct parts of old chats that are no longer accessible. It labels those gaps. Failed receipt or chat creation leaves the source chat and handoff intact.

## Development

The instructions live in [SKILL.md](SKILL.md). The CLI helper is [scripts/start-cli-receiver.py](scripts/start-cli-receiver.py). Test changes in a temporary project before relying on them for live work. The MIT license is in [LICENSE](LICENSE).

This is a GitHub source repository, not an OpenAI plugin-directory listing.
