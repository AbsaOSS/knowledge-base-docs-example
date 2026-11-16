---
title: Agent skill
order: 27
section: Publish Your Docs
---

# The `kb-docs-add` agent skill

An agent skill that onboards a repo's docs for you. It follows the open `SKILL.md`
format, so it works in Claude Code, GitHub Copilot and other readers.

## Install

```bash
# interactive
npx skills add AbsaOSS/knowledge-base --skill kb-docs-add

# non-interactive, project scope, named agents
npx skills add AbsaOSS/knowledge-base --skill kb-docs-add -a claude-code -a github-copilot -y

# user scope
npx skills add AbsaOSS/knowledge-base --skill kb-docs-add -g
```

Or copy the directory by hand:

| Agent | Project | Personal |
|---|---|---|
| Claude Code | `.claude/skills/kb-docs-add/` | `~/.claude/skills/kb-docs-add/` |
| GitHub Copilot | `.github/skills/kb-docs-add/` | `~/.copilot/skills/kb-docs-add/` |
| Open spec | `.agents/skills/kb-docs-add/` | `~/.agents/skills/kb-docs-add/` |

Then ask the agent to "add this repo's docs to the knowledge base".

## Modes

**Onboard.** It classifies the repo and writes the minimum:

| It finds | Type | It writes |
|---|---|---|
| Markdown files, no site generator | single-page | one workflow file |
| A docs site (MkDocs, Starlight, Docusaurus, Jekyll…) | packaged | `kb-docs.json`, the smallest change to make the build headless, one workflow file |
| Docs hosted elsewhere | iframe | nothing; it explains the registry entry |

It pins actions to `@v1`, checks slugs and descriptions against the limits, and tells
you the two steps only you can do: publish a release and register the repo.

**Audit.** For a repo that is already onboarded, it runs the contract checker from a
scratch clone of the Knowledge Base, fixes each finding by [rule ID](rules.md) at its
source (never in built output, never in a third-party theme), and reports what the
checker cannot see, such as URLs built at runtime.
