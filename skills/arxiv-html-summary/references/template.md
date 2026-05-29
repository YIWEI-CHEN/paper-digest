# HTML template reference

This is the visual and structural spec for the paper-summary HTML. Read it before writing any HTML for this skill.

## Aesthetic direction

Dark editorial. Think arxiv-meets-magazine. Cool teal accents on near-black background, with warm orange used sparingly to mark "the paper's own method" rows. Serif font for body/lead text gives it a reading-publication feel; Space Grotesk display font keeps section headings modern.

Do NOT drift toward: generic AI dashboard purple-gradient look, light/airy Notion-style, brutalist all-mono. The aesthetic is settled.

## Fixed components

### `<head>` boilerplate

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{論文短名} 論文導讀</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;900&family=Noto+Sans+TC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
/* full CSS block below */
</style>
</head>
```

### Full CSS block (paste verbatim, then adjust accent colors only if paper topic warrants)

```css
:root{
  --bg:#0d1117;
  --panel:#141b25;
  --panel2:#1b2430;
  --ink:#e8edf4;
  --muted:#93a1b3;
  --line:#26313f;
  --acc:#5ad1c0;       /* primary teal accent */
  --acc2:#f4a259;      /* warm orange — for "ours" rows, key emphasis */
  --acc3:#8c7bff;      /* purple — tertiary, use sparingly */
  --hot:#ff6b6b;       /* red — limitations, warnings */
  --serif:'Noto Serif TC',serif;
  --sans:'Noto Sans TC',sans-serif;
  --mono:'JetBrains Mono',monospace;
  --disp:'Space Grotesk',sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--bg);
  color:var(--ink);
  font-family:var(--sans);
  line-height:1.85;
  font-size:16px;
  background-image:radial-gradient(circle at 12% 8%,rgba(90,209,192,.07),transparent 40%),radial-gradient(circle at 88% 22%,rgba(140,123,255,.08),transparent 42%);
}
.wrap{max-width:980px;margin:0 auto;padding:0 28px}

/* HERO */
header.hero{padding:90px 0 60px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.kicker{font-family:var(--mono);font-size:13px;letter-spacing:.28em;color:var(--acc);text-transform:uppercase;margin-bottom:22px}
h1.title{font-family:var(--disp);font-weight:700;font-size:clamp(38px,6vw,72px);line-height:1.02;letter-spacing:-.02em;color:#fff}
h1.title .sql{color:var(--acc2)}   /* use for highlighting a word in title */
.subtitle{font-family:var(--serif);font-size:clamp(17px,2.4vw,22px);color:var(--muted);margin-top:22px;max-width:680px;font-weight:400}
.meta-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:34px;font-family:var(--mono);font-size:12.5px}
.tag{background:var(--panel2);border:1px solid var(--line);padding:6px 13px;border-radius:999px;color:var(--muted)}
.tag.lit{border-color:var(--acc);color:var(--acc)}
.authors{margin-top:26px;color:var(--muted);font-size:14px}
.authors a{color:var(--acc);text-decoration:none;border-bottom:1px dotted var(--acc)}

/* NAV */
nav.toc{position:sticky;top:0;z-index:20;background:rgba(13,17,23,.82);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:13px 0}
nav.toc .wrap{display:flex;gap:6px;flex-wrap:wrap;font-family:var(--mono);font-size:12.5px}
nav.toc a{color:var(--muted);text-decoration:none;padding:5px 11px;border-radius:7px;transition:.2s}
nav.toc a:hover{color:var(--acc);background:var(--panel2)}

section{padding:62px 0;border-bottom:1px solid var(--line)}
.sec-num{font-family:var(--mono);color:var(--acc);font-size:13px;letter-spacing:.2em}
h2{font-family:var(--disp);font-weight:700;font-size:clamp(26px,4vw,40px);color:#fff;margin:8px 0 28px;letter-spacing:-.01em;line-height:1.1}
h3{font-family:var(--serif);font-weight:600;font-size:21px;color:var(--acc2);margin:34px 0 14px}
p{margin:16px 0;color:var(--ink)}
p.lead{font-family:var(--serif);font-size:18.5px;color:var(--muted)}
strong{color:#fff;font-weight:700}
.hl{color:var(--acc);font-weight:500}
.hl2{color:var(--acc2);font-weight:500}

/* CARDS */
.grid{display:grid;gap:18px;margin:26px 0}
.g2{grid-template-columns:1fr 1fr}
.g3{grid-template-columns:repeat(3,1fr)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px 24px}
.card h4{font-family:var(--disp);font-size:15px;color:var(--acc);margin-bottom:8px;letter-spacing:.02em}
.card p{font-size:14.5px;margin:6px 0;color:var(--muted)}
.card .big{font-family:var(--disp);font-size:34px;color:#fff;font-weight:700}

/* CALLOUT */
.callout{border-left:3px solid var(--acc);background:var(--panel2);padding:18px 24px;border-radius:0 12px 12px 0;margin:24px 0}
.callout.warn{border-color:var(--acc2)}
.callout.hot{border-color:var(--hot)}
.callout p{margin:6px 0}

/* FORMULA */
.formula{font-family:var(--mono);background:#0a0e14;border:1px solid var(--line);border-radius:12px;padding:20px 24px;margin:22px 0;color:var(--acc);font-size:15px;overflow-x:auto}

/* CODE */
pre{background:#0a0e14;border:1px solid var(--line);border-radius:12px;padding:20px 22px;overflow-x:auto;margin:20px 0;font-family:var(--mono);font-size:13px;line-height:1.7}
code{font-family:var(--mono);background:var(--panel2);padding:2px 7px;border-radius:5px;font-size:.88em;color:var(--acc)}
pre code{background:none;padding:0;color:#c8d3e0}
.kw{color:var(--acc3)} .str{color:var(--acc2)} .cmt{color:#5b6675} .fn{color:var(--acc)}

/* TABLE */
.tbl-wrap{overflow-x:auto;margin:22px 0;border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-family:var(--sans)}
caption{caption-side:top;text-align:left;font-family:var(--mono);font-size:12px;color:var(--muted);padding:14px 18px 4px;letter-spacing:.04em}
th,td{padding:11px 15px;text-align:left;border-bottom:1px solid var(--line)}
th{background:var(--panel2);font-family:var(--disp);font-size:12.5px;color:var(--acc);font-weight:700;letter-spacing:.03em}
td{color:var(--muted)}
td.num{font-family:var(--mono);text-align:right;color:var(--ink)}
tr.best td{background:rgba(90,209,192,.08)}
tr.best td.num{color:var(--acc);font-weight:700}
.ours{color:var(--acc2);font-weight:600}

/* DIAGRAM */
.figbox{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:26px;margin:26px 0}
.figcap{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:14px;text-align:center;letter-spacing:.03em}
svg{display:block;width:100%;height:auto}

/* PIPELINE STEPS */
.steps{counter-reset:s;margin:24px 0}
.step{display:flex;gap:18px;padding:18px 0;border-bottom:1px dashed var(--line)}
.step:last-child{border-bottom:none}
.step .n{counter-increment:s;flex:0 0 38px;height:38px;border-radius:10px;background:var(--panel2);border:1px solid var(--acc);color:var(--acc);font-family:var(--disp);font-weight:700;display:flex;align-items:center;justify-content:center}
.step .n::before{content:counter(s)}
.step .body h4{font-family:var(--disp);font-size:16px;color:#fff;margin-bottom:4px}
.step .body p{font-size:14.5px;color:var(--muted);margin:2px 0}

footer{padding:60px 0 90px;text-align:center;color:var(--muted);font-family:var(--mono);font-size:13px}
footer a{color:var(--acc);text-decoration:none}

@media(max-width:720px){
  .g2,.g3{grid-template-columns:1fr}
  .wrap{padding:0 18px}
  section{padding:46px 0}
}
```

## Component patterns

### Hero

```html
<header class="hero">
  <div class="wrap">
    <div class="kicker">{venue} {year} · 論文導讀</div>
    <h1 class="title">{ShortName}</h1>
    <p class="subtitle">{一句話精髓 — 不超過 60 字,點出 paper 的核心 contribution}</p>
    <div class="meta-row">
      <span class="tag lit">{核心概念 1}</span>
      <span class="tag lit">{核心概念 2}</span>
      <span class="tag">{次要 tag}</span>
      <span class="tag">{資料集}</span>
    </div>
    <p class="authors">{作者列表} · {機構} · <a href="{arxiv URL}">arXiv:{id}</a></p>
  </div>
</header>
```

### Sticky TOC

```html
<nav class="toc">
  <div class="wrap">
    <a href="#problem">01 問題定義</a>
    <a href="#method">02 方法論</a>
    ...
  </div>
</nav>
```

Number sections `01`, `02` ... in display order. Each `<section>` gets a matching `id` and `<div class="sec-num">SECTION 0N</div>` at the top.

### Section skeleton

```html
<section id="method">
  <div class="wrap">
    <div class="sec-num">SECTION 02</div>
    <h2>方法論 — Methodology</h2>
    <p class="lead">{一段 lead, serif 字體, 介紹這一節要講什麼}</p>
    ... content ...
  </div>
</section>
```

### Callouts (use for emphasis, not decoration)

```html
<div class="callout">
  <p><strong>關鍵優勢：</strong>...</p>
</div>

<div class="callout warn">  <!-- orange — caveat / known weakness -->
  <p><strong>已知弱點：</strong>...</p>
</div>

<div class="callout hot">  <!-- red — limitation, future work item -->
  <p><strong>限制：</strong>...</p>
</div>
```

### Cards (good for: contribution lists, dataset overviews, metric cards)

```html
<div class="grid g3">
  <div class="card">
    <h4>{Card title}</h4>
    <p>{Short desc}</p>
  </div>
  <div class="card">
    <h4>{Metric name}</h4>
    <p class="big">{Number}</p>
    <p>{Context}</p>
  </div>
  ...
</div>
```

Use `g2` for 2-column, `g3` for 3-column. Below 720px they auto-collapse.

### Formula block

```html
<div class="formula">S = LLM( I , D , Q , E )<br><span style="color:var(--muted)">{notation key}</span></div>
```

Don't try LaTeX. Plain text with `<sub>`/`<sup>` is enough.

### Code blocks with inline syntax highlighting

Apply `.kw .str .cmt .fn` classes manually inside `<pre><code>`:

```html
<pre><code><span class="cmt"># comment</span>
<span class="kw">def</span> <span class="fn">function_name</span>(arg):
    <span class="kw">return</span> <span class="str">"string"</span></code></pre>
```

For SQL: keywords like SELECT, FROM, WHERE wrap in `.kw`; string literals in `.str`; comments in `.cmt`.

### Reproduced data table

Always include a `<caption>` with the original table number ("Table 2 · ..."). Mark the paper's own method rows with `class="best"` on `<tr>` and `class="ours"` on the method name cell. Numbers go in `<td class="num">`.

```html
<div class="tbl-wrap">
  <table>
    <caption>Table 2 · ACT-SQL vs prior in-context methods (Spider dev)</caption>
    <thead><tr><th>LLM</th><th>Method</th><th>API/SQL</th><th>EM</th><th>EX</th><th>TS</th></tr></thead>
    <tbody>
      <tr><td>Codex</td><td>Rajkumar (2022)</td><td class="num">1</td><td class="num">–</td><td class="num">67.0</td><td class="num">55.1</td></tr>
      <tr class="best"><td>GPT-3.5-turbo</td><td class="ours">ACT-SQL (本文)</td><td class="num">1</td><td class="num">62.7</td><td class="num">80.4</td><td class="num">71.4</td></tr>
    </tbody>
  </table>
</div>
```

### Numbered steps (good for: algorithms, pipelines, workflows)

```html
<div class="steps">
  <div class="step"><div class="n"></div><div class="body">
    <h4>{Step title}</h4>
    <p>{Description}</p>
  </div></div>
  ...
</div>
```

The number is auto-incremented via CSS counter — don't write the digits manually.

### Inline SVG diagram pattern

Wrap in `.figbox` with a `.figcap` caption. Use `viewBox` for responsive scaling. Use the CSS variable colors via literal hex (since SVG inside HTML doesn't inherit CSS vars cleanly — use `#5ad1c0`, `#f4a259`, etc. directly). Caption should note what original paper figure it corresponds to.

```html
<div class="figbox">
  <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" font-family="JetBrains Mono, monospace">
    <defs>
      <marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L8,3 L0,6 Z" fill="#5ad1c0"/>
      </marker>
    </defs>
    <!-- nodes: -->
    <rect x="20" y="30" width="180" height="40" rx="8" fill="#1b2430" stroke="#26313f"/>
    <text x="110" y="55" fill="#93a1b3" font-size="13" text-anchor="middle">{Node label}</text>
    <!-- arrows: -->
    <line x1="200" y1="50" x2="278" y2="100" stroke="#5ad1c0" marker-end="url(#arr)"/>
  </svg>
  <div class="figcap">圖 N · {description} (依論文 Figure X 重繪)</div>
</div>
```

### Bar chart pattern

When the paper shows a chart without raw numbers, recreate with approximations and label "趨勢示意":

```html
<div class="figbox">
  <svg viewBox="0 0 700 280" xmlns="http://www.w3.org/2000/svg" font-family="JetBrains Mono, monospace">
    <line x1="60" y1="20" x2="60" y2="220" stroke="#26313f"/>
    <line x1="60" y1="220" x2="660" y2="220" stroke="#26313f"/>
    <!-- y-axis labels, gridlines, bars... use #5ad1c0 for the peak/highlight bar, #3a4658 or #4a7d8c for others -->
    <rect x="350" y="55" width="80" height="165" rx="4" fill="#5ad1c0"/>
    <text x="390" y="240" fill="#5ad1c0" font-size="11" text-anchor="middle" font-weight="700">{label} ★</text>
    ...
  </svg>
  <div class="figcap">圖 N · {description} (依論文 Figure X 重繪,數值為示意)</div>
</div>
```

### Footer

```html
<footer>
  <div class="wrap">
    <p>{Authors} ({Year}) · {Venue}, pp. {pages}</p>
    <p style="margin-top:8px"><a href="{arXiv URL}">arXiv:{id}</a>{ · <a href="{github URL}">程式碼 {github short}</a> if applicable}</p>
    <p style="margin-top:18px;color:#5b6675">本頁為論文導讀摘要,圖表為依論文內容重繪／整理;數值以原論文為準。</p>
  </div>
</footer>
```

## Slug conventions for the output filename

- Use the paper's catchy short name in kebab-case: `act-sql.html`, `react.html`, `flash-attention.html`
- If there's no short name, use first-author surname + topic: `vaswani-attention.html`
- Save to `/mnt/user-data/outputs/<slug>.html`

## Skipping things

You don't have to include every section pattern. Use what fits the paper. A theory paper might be all formulas + callouts. An empirical paper might be all tables + cards. A prompt-engineering paper needs code blocks. Pick what each paper needs.
