"""Build the standalone bilingual ML system-design practice handbook (stdlib only)."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets/ml-system-design-practice"
DEST = ROOT / "summaries/zh-TW/ml-system-design-practice-microsoft-ai.html"

STAGES = [
    ("釐清產品目標", "Clarify product goals", "00–05"),
    ("資料與標籤", "Data & labels", "05–12"),
    ("Baseline／模型", "Baseline & models", "12–22"),
    ("訓練與部署", "Training & deployment", "22–32"),
    ("離線評估／線上實驗", "Offline evaluation & online experiments", "32–40"),
    ("失敗案例與取捨", "Failures & tradeoffs", "40–45"),
]
GROUPS = {
    "core": ("最先練的 3 題", "Start with these 3"),
    "priority": ("第一優先補強", "Priority extensions"),
    "extension": ("依方向補強", "Specialized practice"),
    "transfer": ("共通能力延伸", "Transfer practice"),
    "integrated": ("整合挑戰", "Integrated challenge"),
}
REFS = {
    "dlrm": ("DLRM · sparse features & interactions", "https://arxiv.org/abs/1906.00091", "稀疏類別特徵、embedding 與推薦模型的交互設計。", "Sparse categorical features, embeddings, and recommendation-model interactions."),
    "youtube": ("Deep Neural Networks for YouTube Recommendations", "https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/", "候選生成與排序分工的經典參考；不代表目前線上架構。", "A classic reference for separating candidate generation and ranking, not a claim about the current production architecture."),
    "ragpaper": ("Retrieval-Augmented Generation · Lewis et al.", "https://arxiv.org/abs/2005.11401", "結合檢索式知識與生成模型的研究基礎。", "Research foundation for combining retrieved knowledge with generation."),
    "contextual": ("Anthropic · Contextual Retrieval", "https://www.anthropic.com/engineering/contextual-retrieval", "分塊脈絡、BM25／dense 檢索與 reranking 的實務參考。", "Practical reference for chunk context, BM25/dense retrieval, and reranking."),
    "agents": ("Anthropic · Building Effective Agents", "https://www.anthropic.com/engineering/building-effective-agents", "從簡單 workflow 起步，按需求增加 agent 複雜度。", "Start with simple workflows and add agent complexity when the task calls for it."),
    "clip": ("CLIP · Learning Transferable Visual Models", "https://arxiv.org/abs/2103.00020", "圖文對齊表示的研究參考。", "Research reference for aligned image–text representations."),
    "pinsage": ("PinSage · Web-Scale Recommender Systems", "https://arxiv.org/abs/1806.01973", "結合圖結構與節點特徵的推薦表示。", "Recommendation representations combining graph structure and node features."),
    "bias": ("Unbiased Learning-to-Rank with Biased Feedback", "https://arxiv.org/abs/1608.04468", "曝光偏差與 propensity-based learning-to-rank；修正依賴假設。", "Exposure bias and propensity-based learning to rank; corrections depend on assumptions."),
    "calibration": ("On Calibration of Modern Neural Networks", "https://arxiv.org/abs/1706.04599", "機率校準的概念與研究；不保證任一方法適合所有流量。", "Concepts and research on probability calibration; no method is guaranteed for every traffic distribution."),
    "experiments": ("Microsoft Research · Diagnosing Sample Ratio Mismatch", "https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/", "SRM 是分流或資料品質問題的警訊，需先查原因再解讀實驗效果。", "SRM signals assignment or data-quality problems that must be investigated before interpreting effects."),
    "zero": ("ZeRO · Memory Optimizations", "https://arxiv.org/abs/1910.02054", "以分片減少分散式訓練模型狀態的記憶體重複。", "Sharding model state to reduce memory redundancy in distributed training."),
    "fsdp": ("PyTorch · Fully Sharded Data Parallel", "https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html", "FSDP 的官方實作與教學；API 以目前文件為準。", "Official FSDP implementation guidance; consult current documentation for APIs."),
}


def esc(value):
    return html.escape(value, quote=True)


def rich(value):
    value = esc(value)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)


def label(zh, en):
    return f'<span class="zh" lang="zh-Hant">{esc(zh)}</span><span class="en" lang="en">{esc(en)}</span>'


def bilingual(pair, extra=""):
    def paragraphs(s):
        return "".join(f"<p>{rich(p.strip())}</p>" for p in s.split("~~"))
    return f'<div class="bilingual {extra}"><div class="zh" lang="zh-Hant">{paragraphs(pair[0])}</div><div class="en" lang="en">{paragraphs(pair[1])}</div></div>'


def read_cases():
    cases = []
    for line in (SOURCE_DIR / "ml_system_design_content.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("@ "):
            slug, title, group, topics = [v.strip() for v in line[2:].split("|")]
            cases.append(dict(id=slug, title=title, group=group, topics=topics.split(","), steps=[], deep=[], qa=[]))
            continue
        key, value = line.split(" ", 1)
        pair = [v.strip() for v in value.split(" || ")]
        case = cases[-1]
        if key in ("P", "O", "A", "S"):
            assert len(pair) == 2, (case["id"], key)
        if key == "S":
            case["steps"].append(pair)
        elif key == "D":
            assert len(pair) == 4
            case["deep"].append(pair)
        elif key == "Q":
            assert len(pair) == 4
            case["qa"].append(pair)
        elif key == "R":
            case["refs"] = value.split(",")
        else:
            case[key] = pair
    assert len(cases) == 22
    assert len({c["id"] for c in cases}) == 22
    for c in cases:
        assert len(c["steps"]) == 6, c["id"]
        assert all(c.get(k) for k in ("P", "O", "A", "qa", "refs")), c["id"]
        assert len(c["A"][0].split(" > ")) == len(c["A"][1].split(" > "))
        assert all(r in REFS for r in c["refs"])
    return cases


def render_case(c, i):
    h = [f'<article class="case" id="{c["id"]}" data-group="{c["group"]}">']
    opened = " open" if i == 1 else ""
    h.append(f'<details class="case-detail"{opened}><summary class="case-summary"><span class="case-number">{i:02d}</span><span class="summary-copy"><span class="eyebrow">{label(*GROUPS[c["group"]])}</span><span class="case-title">{esc(c["title"])}</span><span class="topics">{esc(" / ".join(c["topics"]))}</span></span><span class="expand-mark" aria-hidden="true">+</span></summary>')
    h.append('<div class="case-body">')
    h.append(bilingual(c["P"], "prompt"))
    if c["id"] == "shopping":
        h.append('<div class="deep"><h4>' + label("完整深入篇", "Full deep dive") + '</h4>')
        h.append(bilingual(("14 個章節、重畫架構圖、資料與 loss、即時工具、贊助排序、評估與 45 分鐘口說流程。", "14 chapters, original diagrams, data and losses, live tools, sponsorship, evaluation, and a 45-minute rehearsal.")))
        h.append('<p style="margin-top:12px"><a class="deep-dive-link" href="copilot-shopping-assistant-deep-dive.html">Copilot Shopping Assistant — Deep Dive ↗</a></p></div>')
    h.append(f'<h3 class="opening-title">{label("口說開場範例", "Spoken opening")}</h3>')
    h.append(bilingual(c["O"], "opening"))
    h.append(f'<h3>{label("白板資料流", "Whiteboard data flow")}</h3><ol class="architecture">')
    for a, b in zip(c["A"][0].split(" > "), c["A"][1].split(" > ")):
        h.append(f'<li>{label(a,b)}</li>')
    h.append('</ol><div class="steps">')
    for n, (step, heading) in enumerate(zip(c["steps"], STAGES), 1):
        h.append(f'<section class="answer-step"><h3><span class="step-num">{n:02d}</span>{label(heading[0],heading[1])}</h3>{bilingual(step)}</section>')
    h.append('</div>')
    if c["deep"]:
        h.append(f'<h3 class="subhead">{label("深入拆解", "Deep dives")}</h3><div class="deep-grid">')
        for d in c["deep"]:
            h.append(f'<section class="deep"><h4>{label(d[0],d[1])}</h4>{bilingual(d[2:])}</section>')
        h.append('</div>')
    h.append(f'<h3 class="subhead">{label("面試官追問 → 建議回答", "Follow-up questions → suggested answers")}</h3>')
    for q in c["qa"]:
        h.append(f'<details class="followup"><summary>{label(q[0],q[1])}</summary>{bilingual(q[2:])}</details>')
    h.append(f'<div class="case-footer"><div class="case-refs"><span>{label("延伸閱讀", "Further reading")}</span>')
    for r in c["refs"]:
        h.append(f'<a href="#ref-{r}">{esc(r.upper())}</a>')
    h.append(f'</div><label class="practice-check"><input type="checkbox" data-done="{c["id"]}">{label("已口說演練", "Rehearsed aloud")}</label></div></div></details></article>')
    return "".join(h)


def build():
    cases = read_cases()
    case_html = "\n".join(render_case(c, i) for i, c in enumerate(cases, 1))
    nav = []
    for group, names in GROUPS.items():
        nav.append(f'<div class="nav-group"><h3>{label(*names)}</h3>')
        for i, c in enumerate(cases, 1):
            if c["group"] == group:
                nav.append(f'<a href="#{c["id"]}" data-nav="{c["id"]}"><span>{i:02d}</span>{esc(c["title"])}</a>')
        nav.append('</div>')
    refs = []
    for key, (title, url, zh, en) in REFS.items():
        refs.append(f'<li id="ref-{key}"><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(title)} ↗</a>{bilingual((zh,en))}</li>')
    template = (SOURCE_DIR / "ml_system_design_template.html").read_text(encoding="utf-8")
    template = re.sub(r"\{\{([^{}]+?)\|\|([^{}]+?)\}\}", lambda m: label(m[1].strip(), m[2].strip()), template)
    for key, value in (("CASES",case_html),("NAV","".join(nav)),("REFERENCES","".join(refs))):
        template = template.replace("<!--" + key + "-->", value)
    assert "<!--CASES-->" not in template
    assert not re.search(r"job\s+description|\bJD\b|position\s+name|職缺|職稱", template, re.I)
    DEST.write_text(template, encoding="utf-8", newline="\n")
    print(f"Built {DEST}: {len(cases)} cases, {len(cases)*6} bilingual steps, {len(template.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    build()
