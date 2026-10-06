# Threadlift for Codex

简体中文 · [English](README.md)

**交接任务，开启新会话。**

这是一个安装到用户级目录的 Codex Skill，用于把长任务转到新会话。发送 **“交接并新开会话”**，或明确调用 **$session-handoff**。Skill 会保存简明交接记录，在当前 Codex 界面允许的范围内建立接收会话，更新项目记忆，然后等待你的下一条指令。

## 工作流程

1. 旧会话汇总当前任务以及连续交接链，记录决定、完成情况、文件、验证结果、待办和无法恢复的历史缺口。
2. 私有记录存放在当前工作目录的 .codex-handoff/。该目录内的 .gitignore 默认阻止普通 Git 添加；在 Git 项目中，写入前会检查文件是否确实被忽略。
3. 接收会话读取交接，更新 .codex-handoff/project-memory.md，只在项目 AGENTS.md 中加入简短的记忆路径指引，写入接收回执，然后停止等待。
4. 只有确认接收回执后，而且能准确识别旧会话时，才归档旧会话。

此流程由你发送指令触发。关闭会话或上下文接近上限本身不会自动触发。

## 各端支持情况

| 界面 | 接收会话 | 之后需要做什么 |
| --- | --- | --- |
| Codex 桌面版 | 能保持原工作目录时，自动创建项目新会话并核验回执 | 在打开的新会话中继续 |
| Codex CLI | 在同一目录自动启动新的、持久保存的非交互会话并核验回执 | 使用输出的会话 ID 和 codex resume 打开交互界面 |
| Codex IDE 扩展 | 保存交接文档及准确的接收首任务 | 自己新建 IDE 聊天，粘贴首任务 |

目前没有核实到 IDE 扩展可供 Skill 自动新建并切换聊天的接口。桌面版遇到无法保持原 worktree 的情况会停止，避免新会话看不到未提交的修改。CLI 能自动创建接收会话；当前终端若要显示它，仍需执行 resume 命令。

## 安装一次，后续项目通用

如果你使用打包版本，解压 `codex-threadlift.zip`，把其中完整的 `session-handoff/` 文件夹放进用户级 Skill 目录。**不要只复制 SKILL.md**；CLI 流程还需要 `scripts/`。

此版本已在 `~/.codex/skills/session-handoff/` 用户级目录验证。使用 macOS/Linux 时，进入解压后的 `session-handoff/` 所在目录，再运行：

    mkdir -p ~/.codex/skills
    cp -R session-handoff ~/.codex/skills/

如果目标文件夹已存在，请先比较版本并合并或替换，不要重复运行复制命令造成嵌套目录。其他 Codex 安装也可能采用 `~/.agents/skills/session-handoff/` 作为用户级目录；请以自己安装版本的 [官方技能说明](https://learn.chatgpt.com/docs/build-skills) 和技能列表为准。安装后新开 Codex 会话；如果没有显示，再重启 Codex。

也可以直接从仓库克隆到用户级目录：

    git clone https://github.com/EricZihaoHe/codex-threadlift.git ~/.codex/skills/session-handoff

安装在用户级目录后，同一用户的不同本地项目和新会话都可使用。Skill 的调用名称仍为 `session-handoff`。

在项目会话中发送：

    $session-handoff 交接并新开会话

直接发送中文触发语也会匹配 Skill 描述，但显式调用更可靠。必须能确定当前本地项目。接收会话不会自行继续旧任务的待办。

## 隐私与项目文件

本公开仓库只放通用指令和 CLI 辅助脚本。**不要把真实 handoff、项目记忆、会话记录、密钥或私人项目文件提交到本仓库。**运行时的 .codex-handoff/ 默认位于你自己的项目并被 Git 忽略。强制添加或原本已追踪的文件可能绕过忽略规则，公开项目前仍应检查 Git 变更。

项目记忆文件供接收会话即时读取，不等同于 Codex 在后台生成的个人记忆。AGENTS.md 只保存“若文件存在则读取”的路径指引，不复制私人记忆内容。

## 要求与限制

- Codex 已启用用户级 Skill。
- CLI 路线需要 Python 3.9+ 和 codex 命令。
- 本地项目目录可写，用于交接和回执。
- 桌面路线需要 Codex 的项目与会话工具。

无法访问的旧会话原文不会被臆测补全，交接中会标记缺口。创建或接收失败时会保留旧会话和交接文档。

## 开发

工作指令见 [SKILL.md](SKILL.md)，CLI 辅助脚本见 [scripts/start-cli-receiver.py](scripts/start-cli-receiver.py)，[LICENSE](LICENSE) 使用 MIT 许可证。修改后先在临时项目测试完整流程。

这是 GitHub 源码仓库，并非 OpenAI 插件目录条目。
