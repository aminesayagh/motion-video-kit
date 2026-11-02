# History: the Codex orchestra (superseded)

These are the files of the first orchestration setup, kept as they were (paths shortened to the project folder):
four local Codex sessions, one per role, each with only its own ArtCraft tool through MCP, driven by
`run.sh brief <role> <brief.md>`. `common.md` holds the rules for every role, `roles/*.md` each role's own;
`run.sh` joined them into an `AGENTS.md` per role before every run.

`editor_common_claude.md` is the rules file written when the editor work moved to Claude subagents; its
"Audio check" and "Group fades" sections came from real failures.

Why it was replaced, and what replaced it: docs/05-orchestration.md. Some details here are out of date
(the voice was Kokoro, then Chatterbox, then Qwen3-TTS cloning; the prompt wording changed from "then" to "and").
