---
name: arxiv-html-summary
description: Produce a self-contained, visually polished HTML summary of an academic paper from an arXiv link (or any paper URL). Use this skill whenever the user shares an arXiv URL, ACL Anthology link, OpenReview link, or paper PDF and asks for a summary, write-up, breakdown, "整理", "導讀", "讀這篇 paper", "html summary", or anything similar — even casually. Defaults to Traditional Chinese narrative with English preserved for code, SQL, formulas, and technical terms. Pulls full paper body via web_fetch, fetches the GitHub repo for actual prompt/code source when relevant, and outputs ONE polished standalone HTML file with TOC, inline SVG diagrams, reproduced data tables, and a dark editorial aesthetic — no external assets, no hotlinked images.
---

# arXiv HTML Summary

Produce a single self-contained HTML file that summarizes an academic paper end-to-end: problem statement, methodology, datasets, experiments with reproduced tables, limitations / future work, and — when a code repo is linked — actual prompt or algorithm source extracted from GitHub.

## When to use

Trigger on any of these signals:

- User shares an arXiv link (`arxiv.org/abs/...` or `arxiv.org/pdf/...`)
- User shares ACL Anthology, OpenReview, NeurIPS, or other paper venue URL
- User uploads or links to a paper PDF
- User says things like "讀這篇 paper", "整理", "導讀", "summary", "幫我看這篇", "深入讀"
- User asks for an HTML write-up of a paper

If the user only asks a *question about* a paper (e.g. "what does X mean") without asking for a written summary, do not trigger — just answer.

## Core workflow

### 1. Fetch the paper body

The arXiv abstract page (`/abs/`) only gives you the abstract. **Always** fetch `/pdf/` for full body. ACL Anthology and OpenReview pages usually need a follow-up fetch to the PDF link.

```
web_fetch("https://arxiv.org/pdf/<id>")
```

If rate-limited, fall back to ACL Anthology or the HTML mirror at `ar5iv.labs.arxiv.org/html/<id>`. If you get only the abstract, say so and ask the user whether to proceed with a thinner summary or try again.

Read the full body before writing anything. Pay attention to: section structure, all tables (especially the main results table), figure captions (figures themselves rarely render but their captions tell you what to recreate), evaluation metrics, hyperparameters, ablation studies, limitations section.

### 2. Check for a code repo

If the paper mentions a GitHub URL (commonly in a footnote on page 1, in the abstract, or under "Code"), fetch it. The README often lists key files. If the paper is method-heavy (introduces a new prompt, algorithm, training recipe), **clone the repo and read the actual source**:

```
git clone --depth=1 <repo-url> /home/claude/<reponame>
```

This matters a lot for prompt-engineering papers, agent papers, training recipe papers — the appendix's "Prompt template" rarely matches what's actually in the code. The code is the truth. Quote it directly in the HTML, not the appendix version.

If the user later asks "find their prompts" / "show me the code" as a follow-up, you should already have the repo cloned. If not, do it then.

### 3. Decide structure

Default section order — adapt to what the paper actually has:

1. **問題定義 / Problem Statement** — what task, why prior work falls short, paper's contributions
2. **方法論 / Methodology** — core ideas, formalization, any equations
3. **核心貢獻** — if the paper has one signature contribution (a new prompt, a new module, a new algorithm), give it its own section with a recreated diagram and a worked example
4. **資料集 / Datasets** — what they use, why, evaluation metrics
5. **實驗結果 / Experiments** — reproduce the main results table verbatim; include ablations if they're load-bearing; flag the "ours" rows
6. **(Optional) Prompt 原始碼 / Implementation** — only if the user asks, or if it's a prompt-engineering paper where the code is the contribution
7. **限制與未來工作 / Limitations & Future Work** — explicitly mark what the authors call out

Skip sections that don't apply. Add sections that do (e.g. "Threat model" for security papers, "Training recipe" for pretraining papers). Don't pad.

### 4. Build the HTML

**Always** read `references/template.md` before writing the HTML — it has the full CSS, layout, and component patterns to use. It is the source of truth for the visual style.

Key non-negotiables:

- **One file**, no external assets. Fonts come from Google Fonts via CDN (`<link>`); everything else is inline.
- **Self-contained figures**: recreate key diagrams as inline SVG. Do NOT hotlink arxiv figure images — they often won't render and break the file's portability. Reproduce charts (bar charts, line charts) as inline SVG with the actual paper numbers when given, or clearly mark "趨勢示意" if the paper only shows a figure without raw numbers.
- **Reproduce data tables verbatim** with paper numbers — don't paraphrase the data. Highlight the paper's own method row (use `class="best"` and `class="ours"` per the template).
- **Traditional Chinese narrative**, but keep English for: code, SQL, table column headers when they're proper nouns, model names, dataset names, technical terms that have no clean Chinese rendering, and inline citations.
- **TOC sticky nav at top** with section numbers.
- **Hero section** with paper title, subtitle (one-line essence), tag chips for key concepts, authors + arXiv link.
- **Code blocks** must preserve syntax highlighting via the inline `.kw .str .cmt .fn` classes in the template — apply them by hand around tokens.

### 5. Save and present

Save to `/mnt/user-data/outputs/<slug>.html` directly. Slug = short identifier (e.g. `act-sql`, `react`, `flash-attention`). Use `present_files` to share. Keep the closing message brief — list which sections the file contains and call out anything notable you decided about scope (e.g. "I skipped the appendix ablation tables since they're not load-bearing; let me know if you want them added").

## Style guidance for the narrative

- Write as a knowledgeable colleague explaining the paper to a peer — not a marketing summary, not a textbook chapter.
- Use callout boxes (`.callout`, `.callout.warn`, `.callout.hot` per template) to highlight: the paper's core trick, surprising results, known limitations, common misreadings.
- Quote at most one short phrase per source per paper section (copyright). For data tables, reproducing numbers + column headers is fine — those are facts, not prose.
- When the paper presents a formula, render it in a `.formula` block — don't try to render LaTeX, write it in plain notation.
- When the paper has a worked example (a sample prompt, a case study), include it. Worked examples are what make summaries useful.

## What to do if the user iterates

If the user asks for a follow-up after the first HTML is delivered — "now add their prompts", "go deeper on X", "translate to English" — **append or modify the existing HTML file in place**, don't make a new one. Update the TOC and section numbers accordingly. Re-present the same file.

## What NOT to do

- Don't paste arxiv figure URLs as `<img src>`. They break.
- Don't produce a markdown file when the user asked for HTML.
- Don't generate a generic-looking "AI summary" page. The template's editorial aesthetic is intentional — keep it.
- Don't pad sections that the paper doesn't actually cover (e.g. inventing "future work" the authors didn't mention).
- Don't fabricate numbers. If a paper shows a figure without raw values, recreate the chart with "趨勢示意" / "illustrative" labeled and explain that in the figure caption.
- Don't ask the user to confirm before starting. The trigger is clear; just start. The exception is if the URL fetch fails — then surface the problem.
