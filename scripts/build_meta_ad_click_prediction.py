"""Build an offline bilingual CTR deep dive using the shopping guide's renderers."""
from pathlib import Path
import json
import re

from build_copilot_shopping_assistant import esc, label, pair_text, node, render_block

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/meta-ad-click-prediction-deep-dive"
DEST = ROOT / "summaries/zh-TW/meta-ad-click-prediction-deep-dive.html"


def diagram(name, spec):
    title = " / ".join(spec["title"])
    h = [f'<figure class="diagram"><div class="diagram-scroll" tabindex="0" role="region" aria-label="{esc(title)}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 {spec["height"]}" role="img" aria-labelledby="diagram-title-{name}"><title id="diagram-title-{name}">{esc(title)}</title><defs><marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#55766a"/></marker></defs>']
    for path in spec["paths"]:
        h.append(f'<path d="{esc(path)}" fill="none" stroke="#55766a" stroke-width="2" stroke-linejoin="round" marker-end="url(#arrow-{name})"/>')
    h.extend(node(*args) for args in spec["nodes"])
    h.append('</svg></div><figcaption>' + label(spec["caption"]) + '</figcaption></figure>')
    return "".join(h)


def calculator():
    h = ['<div class="sampling-lab block"><h3>' + label(["抽樣如何改變 pCTR？", "How does sampling change pCTR?"]) + '</h3><div class="sampling-inputs">']
    for key, title, value, minimum in (
        ("sample-q", ["抽樣模型機率 q", "Sampled-model probability q"], ".1", "0"),
        ("sample-s1", ["正樣本保留率 s₁", "Positive retention s₁"], "1", ".000001"),
        ("sample-s0", ["負樣本保留率 s₀", "Negative retention s₀"], ".1", ".000001"),
    ):
        h.append(f'<label for="{key}">{label(title)}<input id="{key}" type="number" min="{minimum}" max="1" step="any" value="{value}" inputmode="decimal"></label>')
    h.append('</div><p>' + label(["修正後的機率 p", "Corrected probability p"]) + ': <output id="corrected-p" aria-live="polite">1.0989%</output></p>')
    h.append('<p id="sampling-error" hidden role="status">' + label(["q 必須介於 0 與 1；保留率必須大於 0 且不超過 1。", "q must be between 0 and 1; retention rates must be greater than 0 and at most 1."]) + '</p>')
    h.append(pair_text(["互動計算只示範 Bayes 修正；假設保留率只依 label、q 在抽樣分布已校準，且未另外用 inverse weighting 修正。", "This calculator demonstrates Bayes correction only: retention depends on the label, q is calibrated on the sampled distribution, and inverse weighting has not already corrected the model."]))
    h.append('</div>')
    return "".join(h)


def build():
    data = json.loads((ASSETS / "content.json").read_text(encoding="utf-8"))
    diagrams = json.loads((ASSETS / "diagrams.json").read_text(encoding="utf-8"))
    sections, sources = data["sections"], data["sources"]
    assert len(sections) == 14 and len({s["id"] for s in sections}) == 14
    assert len({s["id"] for s in data["scenarios"]}) == len(data["scenarios"])
    assert "normal" in {s["id"] for s in data["scenarios"]}
    nav, options, body = [], [], []
    for n, s in enumerate(sections, 1):
        nav.append(f'<a href="#{s["id"]}"><span class="nav-no">{n:02}</span>{label(s["title"])}</a>')
        options.append(f'<option value="{s["id"]}" data-zh="{esc(s["title"][0])}" data-en="{esc(s["title"][1])}">{esc(s["title"][0])}</option>')
        body.append(f'<section class="section" id="{s["id"]}"><div class="section-kicker">{n:02} / {s["id"].upper()}</div><h2>{label(s["title"])}</h2>{pair_text(s["lead"], "lede")}')
        for b in s["blocks"]:
            if b["type"] == "diagram":
                body.append(diagram(b["name"], diagrams[b["name"]]))
            elif b["type"] == "calculator":
                body.append(calculator())
            else:
                body.append(render_block(b, data["scenarios"]))
        body.append('<div class="section-refs">' + label(["概念／程式來源", "Concept / code sources"]))
        for ref in s["refs"]:
            assert ref in sources, ref
            body.append(f'<a href="#ref-{ref}">{esc(ref.upper())}</a>')
        body.append('</div></section>')
    refs = ['<section class="section" id="sources"><div class="section-kicker">15 / READING & CODE</div><h2>' + label(["來源與程式碼導讀", "Sources and code reading"]) + '</h2>' + pair_text(["依序讀：FB14 的資料閉環 → FTRL／DeepFM／DCNv2 的 baseline → DIN 與 Meta 序列建模 → serving 與 robustness。教學文章用來練組織；原始論文與程式用來核對技術。各章架構、例子、數字與實驗方案是本篇的設計綜合。", "Read in order: FB14's learning loop → FTRL/DeepFM/DCNv2 baselines → DIN and Meta sequence modeling → serving and robustness. Teaching articles help structure an answer; original papers and code ground the technical details. Architectures, examples, numbers, and experiment plans in this guide are a design synthesis."], "lede") + '<ol class="source-list">']
    for key, source in sources.items():
        refs.append(f'<li id="ref-{key}"><a class="source-title" href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(source["title"])} ↗</a><div class="source-meta">{esc(source["kind"])}</div>{pair_text(source["note"])}</li>')
    refs.append('</ol></section>')
    output = (ASSETS / "template.html").read_text(encoding="utf-8")
    output = re.sub(r"\{\{([^{}]+?)\|\|([^{}]+?)\}\}", lambda m: label([m[1].strip(), m[2].strip()]), output)
    for key, values in (("NAV", nav), ("OPTIONS", options), ("SECTIONS", body), ("SOURCES", refs)):
        output = output.replace(f"<!--{key}-->", "\n".join(values))
    assert not re.search(r"job\s+description|\bJD\b|position\s+name|職缺|職稱", output, re.I)
    assert not re.search(r"<!--(?:NAV|OPTIONS|SECTIONS|SOURCES)-->|\{\{", output)
    assert output.count('<svg ') == 3
    DEST.write_text(output, encoding="utf-8", newline="\n")
    print(f"Built {DEST.name}: {len(sections)} chapters, {len(sources)} sources, 3 original SVGs, {len(output.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    build()
