"""Build the self-contained bilingual product recommendation guide (stdlib only)."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/amazon-product-recommendation-deep-dive"
DEST = ROOT / "summaries/zh-TW/amazon-product-recommendation-deep-dive.html"


def esc(value):
    return html.escape(str(value), quote=True)


def label(pair):
    assert len(pair) == 2 and all(isinstance(x, str) and x for x in pair)
    return f'<span class="label"><span class="zh" lang="zh-Hant">{esc(pair[0])}</span><span class="en" lang="en">{esc(pair[1])}</span></span>'


def pair_text(pair, extra=""):
    assert len(pair) == 2 and all(pair)
    return f'<div class="pair {extra}"><p class="zh" lang="zh-Hant">{esc(pair[0])}</p><p class="en" lang="en">{esc(pair[1])}</p></div>'


def node(x, y, zh, en, tone="white", width=280):
    fills = {"white": "#ffffff", "teal": "#dceee5", "amber": "#fff0d4", "navy": "#183b49"}
    color = "#f6faf4" if tone == "navy" else "#193b43"
    return (f'<rect x="{x}" y="{y}" width="{width}" height="66" rx="8" fill="{fills[tone]}" stroke="#a6beb2"/>'
            f'<text class="zh" lang="zh-Hant" x="{x+width/2}" y="{y+27}" fill="{color}" text-anchor="middle" font-size="15" font-weight="600">{esc(zh)}</text>'
            f'<text class="en" lang="en" x="{x+width/2}" y="{y+47}" fill="{color}" text-anchor="middle" font-size="12">{esc(en)}</text>')


def diagram(name):
    """Original vector layouts: conceptual synthesis, never copied source artwork."""
    if name == "online":
        height = 640
        title = "多階段線上推薦 / Multistage online recommendation"
        nodes = [
            (390, 20, "請求、使用者與 session", "Request / user / session", "navy", 300),
            (40, 128, "Item-to-item 與熱門／探索", "Item-to-item + popular / explore", "teal", 300),
            (390, 128, "Two-tower 向量召回", "Two-tower ANN retrieval", "teal", 300),
            (740, 128, "Session 與互補候選", "Session / complementary retrieval", "teal", 300),
            (390, 235, "合併、去重、初步資格查驗", "Merge + early qualification ~1,000", "white", 300),
            (390, 340, "輕量排序 → 精排", "Light rank → rich rank ~200", "white", 300),
            (740, 340, "批次特徵、最新供給", "Batch features + fresh supply", "amber", 300),
            (390, 445, "最終查驗與清單策略", "Final qualification + slate policy", "white", 300),
            (40, 445, "有界補取／合格備選", "Bounded refill / eligible fallback", "amber", 300),
            (390, 550, "最多 20 個商品 → 實際曝光", "Up to 20 items → actual exposures", "navy", 300),
            (740, 550, "版本、曝光與後續結果日誌", "Version / exposure / outcome logs", "white", 300),
        ]
        paths = ["M540 86V128", "M540 104H190V128", "M540 104H890V128",
                 "M190 194V217H460V235", "M540 194V235", "M890 194V217H620V235",
                 "M540 301V340", "M740 373H690", "M890 406V478H690",
                 "M540 406V445", "M540 511V550", "M390 466H340", "M340 492H390",
                 "M690 583H740"]
        caption = ["圖 1 · 原創架構。綜合 Amazon item-to-item、NVIDIA 候選／排序流程與 two-tower 公開概念。候選數均為設計假設；實際曝光由渲染事件確認，不能用 API 回傳代替。",
                   "Figure 1 · Original architecture synthesizing public Amazon item-to-item, NVIDIA candidate/ranking, and two-tower concepts. Counts are design assumptions. Rendering events confirm actual exposures; API responses are not exposure evidence."]
    elif name == "offline":
        height = 560
        title = "資料、訓練與發布閉環 / Data, training, and release loop"
        nodes = [
            (40, 24, "曝光／互動／交易事件", "Exposure / interaction / transactions", "white", 300),
            (390, 24, "商品／供給的歷史版本", "Historical catalog / supply versions", "white", 300),
            (740, 24, "時間切分與資料契約", "Temporal splits + data contracts", "white", 300),
            (390, 138, "當時可用特徵＋成熟標籤", "As-known features + mature labels", "teal", 300),
            (40, 252, "Retriever 與版本化索引", "Retriever + versioned item index", "teal", 300),
            (390, 252, "Serving-like 候選與 ranker", "Serving-like candidates + ranker", "teal", 300),
            (740, 252, "評估、校準與策略 gate", "Evaluation / calibration / policy gate", "amber", 300),
            (390, 365, "相容版本一起發布／回滾", "Compatible bundle + rollback", "navy", 300),
            (390, 478, "影子流量 → 小流量 → A/B", "Shadow → canary → A/B", "white", 300),
        ]
        paths = ["M190 90V116H460V138", "M540 90V138", "M890 90V116H620V138",
                 "M470 204V226H190V252", "M540 204V252", "M340 285H390", "M690 285H740",
                 "M190 318V398H390", "M540 318V365", "M890 318V398H690", "M540 431V478",
                 "M390 511H18V57H40"]
        caption = ["圖 3 · 原創資料閉環。歷史特徵需符合當時可用性，標籤需成熟；retriever、index 與 ranker 以相容版本發布。底部回流是診斷與下一輪資料，並非讓測試答案流回當輪訓練。",
                   "Figure 3 · Original data loop. Historical features respect availability, labels mature, and retrieval/index/ranking versions remain compatible. Feedback supports diagnosis and future data cycles; it does not leak test answers into the current training run."]
    elif name == "towers":
        height = 680
        title = "Two-tower 訓練與服務 / Two-tower training and serving"
        nodes = [
            (130, 28, "使用者／session prefix", "User / session prefix", "white", 300),
            (650, 28, "正例與抽樣商品內容", "Positive + sampled item content", "white", 300),
            (130, 140, "Query encoder → q", "Query encoder → q", "teal", 300),
            (650, 140, "Item encoder → v", "Item encoder → v", "teal", 300),
            (390, 253, "對比 loss、抽樣與正例遮罩", "Contrastive loss + sampling / masks", "amber", 300),
            (40, 386, "線上 context → query encoder", "Online context → query encoder", "white", 320),
            (720, 386, "離線 item encoder → 全商品", "Offline item encoder → all items", "white", 320),
            (40, 502, "當前 query 向量", "Current query vector", "teal", 320),
            (720, 502, "相容版本的 ANN 索引", "Compatible ANN index", "teal", 320),
            (390, 594, "相似度搜尋 → 候選 ID", "Similarity search → candidate IDs", "navy", 300),
        ]
        paths = ["M280 94V140", "M800 94V140", "M280 206V286H390", "M800 206V286H690",
                 "M200 452V502", "M880 452V502", "M200 568V627H390", "M880 568V627H690"]
        caption = ["圖 2 · 原創 two-tower 圖。上半部是訓練，下半部是相容模型發布後的服務。線上只編碼 query；商品向量預計算。訓練用抽樣校正不等於線上必須套相同分數校正。",
                   "Figure 2 · Original two-tower diagram. Training is above; serving after a compatible release is below. Encode only the query online and precompute item vectors. Training-time sampling correction does not automatically define serving-time score correction."]
    else:
        raise ValueError(name)
    parts = [f'<figure class="diagram"><div class="diagram-scroll" tabindex="0" role="region" aria-label="{esc(title)}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 {height}" role="img" aria-labelledby="diagram-title-{name}"><title id="diagram-title-{name}">{esc(title)}</title><defs><marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#55766a"/></marker></defs>']
    if name == "towers":
        parts.append('<path d="M40 349H1040" stroke="#a6beb2" stroke-dasharray="7 6"/>')
    parts.extend(f'<path d="{path}" fill="none" stroke="#55766a" stroke-width="2" stroke-linejoin="round" marker-end="url(#arrow-{name})"/>' for path in paths)
    parts.extend(node(*args) for args in nodes)
    parts.append('</svg></div><figcaption>' + label(caption) + '</figcaption></figure>')
    return "".join(parts)


def render_scenarios(scenarios):
    h = ['<div class="block"><div class="scenario-buttons" role="group" aria-label="Scenario selector">']
    for s in scenarios:
        h.append(f'<button type="button" data-scenario-button="{s["id"]}" aria-controls="scenario-{s["id"]}" aria-pressed="false">{label(s["label"])}</button>')
    h.append('</div>')
    for s in scenarios:
        h.append(f'<section class="scenario-panel" id="scenario-{s["id"]}" data-scenario-panel="{s["id"]}" aria-labelledby="scenario-title-{s["id"]}"><h3 id="scenario-title-{s["id"]}">{label(s["title"])}</h3>')
        for key, heading in (("facts", ["觀察到的資料", "OBSERVED INPUT"]), ("decision", ["系統應採取的決策", "EXPECTED DECISION"])):
            h.append(f'<div class="scenario-row"><div class="scenario-label">{label(heading)}</div>{pair_text(s[key])}</div>')
        h.append(pair_text(s["check"], "scenario-check") + '</section>')
    return "".join(h) + '</div>'


def render_block(b, scenarios):
    t = b["type"]
    if t == "p":
        return pair_text(b["text"], "block")
    if t == "callout":
        return f'<div class="callout block"><h3>{label(b["title"])}</h3>{pair_text(b["text"])}</div>'
    if t == "cards":
        return '<div class="cards block">' + "".join(f'<div class="card"><h3>{label(c["title"])}</h3>{pair_text(c["text"])}</div>' for c in b["items"]) + '</div>'
    if t == "table":
        assert all(len(row) == len(b["headers"]) for row in b["rows"])
        return '<div class="table-wrap block" tabindex="0" role="region" aria-label="Comparison table"><table><thead><tr>' + "".join(f'<th scope="col">{label(h)}</th>' for h in b["headers"]) + '</tr></thead><tbody>' + "".join('<tr>' + "".join(f'<td>{label(cell)}</td>' for cell in row) + '</tr>' for row in b["rows"]) + '</tbody></table></div>'
    if t == "formula":
        return f'<pre class="formula block"><code>{esc(b["text"])}</code></pre>'
    if t == "code":
        return f'<div class="block"><div class="code-caption">{label(b["caption"])}</div><pre><code>{esc(b["code"])}</code></pre></div>'
    if t == "qa":
        return f'<details class="followup"><summary>{label(b["q"])}</summary>{pair_text(b["a"])}</details>'
    if t == "diagram":
        return diagram(b["name"])
    if t == "scenarios":
        return render_scenarios(scenarios)
    raise ValueError(t)


def build():
    data = json.loads((ASSETS / "content.json").read_text(encoding="utf-8"))
    sources = json.loads((ASSETS / "sources.json").read_text(encoding="utf-8"))
    sections = data["sections"]
    assert len(sections) == 15 and len({s["id"] for s in sections}) == 15
    assert len(data["scenarios"]) == 5 and len({s["id"] for s in data["scenarios"]}) == 5
    nav, options, body = [], [], []
    for n, s in enumerate(sections, 1):
        nav.append(f'<a href="#{s["id"]}"><span class="nav-no">{n:02}</span>{label(s["title"])}</a>')
        options.append(f'<option value="{s["id"]}" data-zh="{esc(s["title"][0])}" data-en="{esc(s["title"][1])}">{esc(s["title"][0])}</option>')
        body.append(f'<section class="section" id="{s["id"]}"><div class="section-kicker">{n:02} / {s["id"].upper()}</div><h2>{label(s["title"])}</h2>{pair_text(s["lead"], "lede")}')
        body.extend(render_block(b, data["scenarios"]) for b in s["blocks"])
        body.append('<div class="section-refs">' + label(["概念／程式來源", "Concept / code sources"]))
        for ref in s["refs"]:
            assert ref in sources
            body.append(f'<a href="#ref-{ref}">{esc(ref.upper())}</a>')
        body.append('</div></section>')
    refs = ['<section class="section" id="sources"><div class="section-kicker">16 / READING & CODE</div><h2>' + label(["來源與程式碼導讀", "Sources and code reading"]) + '</h2>' + pair_text(["以下區分原始研究、官方文件、程式與教學框架。來源支援各自概念；本篇整合架構、假設數字、案例與口說稿為自行整理。未複製來源圖，也未宣稱取得 Amazon 現行內部架構或執行模型訓練。外部連結需網路，正文與圖表可離線閱讀。", "The list distinguishes original research, official documentation, code, and teaching frameworks. Each supports specific concepts; the integrated architecture, assumed numbers, scenarios, and scripts are original synthesis. No source artwork was copied, no current internal Amazon architecture is claimed, and no model training was run. External links need a network; text and diagrams work offline."], "lede") + '<ol class="source-list">']
    for key, (title, url, kind, zh, en) in sources.items():
        refs.append(f'<li id="ref-{key}"><a class="source-title" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(title)} ↗</a><div class="source-meta">{esc(kind)}</div>{pair_text([zh, en])}</li>')
    refs.append('</ol></section>')
    output = (ASSETS / "template.html").read_text(encoding="utf-8")
    output = re.sub(r"\{\{([^{}]+?)\|\|([^{}]+?)\}\}", lambda m: label([m[1].strip(), m[2].strip()]), output)
    for key, value in (("NAV", nav), ("OPTIONS", options), ("SECTIONS", body), ("SOURCES", refs)):
        output = output.replace(f"<!--{key}-->", "\n".join(value))
    assert not re.search(r"job\s+description|\bJD\b|position\s+name|職缺|職稱", output, re.I)
    assert not re.search(r"<!--(?:NAV|OPTIONS|SECTIONS|SOURCES)-->|\{\{", output)
    DEST.write_text(output, encoding="utf-8", newline="\n")
    print(f"Built {DEST.name}: {len(sections)} chapters, {len(sources)} sources, {len(output.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    build()
