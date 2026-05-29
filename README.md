# paper-digest

Bilingual (Traditional Chinese / English) HTML summaries of papers I'm reading.

🌐 **Live site:** https://yiwei-chen.github.io/paper-digest/

## Structure

```
paper-digest/
├── index.html              # Landing page listing all summaries
├── summaries/
│   ├── zh-TW/              # Traditional Chinese summaries
│   │   └── <paper-slug>.html
│   └── en/                 # English summaries
│       └── <paper-slug>.html
├── assets/                 # Shared CSS / images / fonts
└── skills/
    └── arxiv-html-summary/ # Copilot CLI skill used to generate summaries
```

## Naming convention

`<year>-<first-author>-<short-title-slug>.html`

Example: `2024-caferoglu-esql.html`

## Adding a new summary

1. Drop the HTML file into `summaries/zh-TW/` and/or `summaries/en/`.
2. Add a row to the table in `index.html`.
3. Commit and push — GitHub Pages will deploy automatically.

## Generating summaries

Self-contained HTML files are generated with the [`arxiv-html-summary`](skills/arxiv-html-summary/SKILL.md)
skill, vendored under [`skills/arxiv-html-summary/`](skills/arxiv-html-summary/).
Each report is a single standalone file with inline CSS/SVG — no external
assets, no hotlinked images.

### Wiring the skill into a CLI

The skill is a portable bundle (`SKILL.md` + `references/`) usable from GitHub
Copilot CLI, Claude Code, or any tool that loads skill folders. Symlink (or
junction on Windows) it into your tool's skills directory:

```powershell
# GitHub Copilot CLI
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.copilot\skills\arxiv-html-summary" `
  -Target "$PWD\skills\arxiv-html-summary"

# Claude Code
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.claude\skills\arxiv-html-summary" `
  -Target "$PWD\skills\arxiv-html-summary"
```

```bash
# macOS / Linux
ln -s "$PWD/skills/arxiv-html-summary" ~/.copilot/skills/arxiv-html-summary
ln -s "$PWD/skills/arxiv-html-summary" ~/.claude/skills/arxiv-html-summary
```

After wiring, ask your CLI to "summarize https://arxiv.org/abs/<id>" and it
will invoke the skill automatically.
