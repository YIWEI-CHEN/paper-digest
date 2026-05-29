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
└── papers/                 # Original PDFs (optional, gitignored if large)
```

## Naming convention

`<year>-<first-author>-<short-title-slug>.html`

Example: `2024-caferoglu-esql.html`

## Adding a new summary

1. Drop the HTML file into `summaries/zh-TW/` and/or `summaries/en/`.
2. Add a row to the table in `index.html`.
3. Commit and push — GitHub Pages will deploy automatically.

## Generating summaries

Self-contained HTML files are generated with the `arxiv-html-summary` skill in
the GitHub Copilot CLI. Each report is a single standalone file with inline
CSS/SVG — no external assets, no hotlinked images.
