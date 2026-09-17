"""Build the self-contained bilingual shopping-assistant deep dive (stdlib only)."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/copilot-shopping-assistant-deep-dive"
DEST = ROOT / "summaries/zh-TW/copilot-shopping-assistant-deep-dive.html"

# Short source notes describe what is public; the worked design remains a synthesis.
SOURCES = {
    "rufus": ("Amazon Science · The technology behind Rufus", "https://www.amazon.science/blog/the-technology-behind-amazons-genai-powered-shopping-assistant-rufus", "2024 · engineering article", "讀多來源 RAG、Stores APIs、streaming 與 hydration；不是完整公開的排序／廣告系統。", "Read multi-source RAG, Stores APIs, streaming, and hydration; this is not a complete ranking/ad-system specification."),
    "aws": ("AWS · Generative AI Shopping Assistant", "https://github.com/aws-solutions-library-samples/guidance-for-generative-ai-shopping-assistant-using-agents-for-amazon-bedrock", "reference implementation + architecture", "先讀 README 架構，再讀 source/retail_ai_assistant_app。示範以 knowledge base 與 action groups 串接；本篇圖重新繪製並加入驗證與贊助邊界。", "Start with the README architecture, then source/retail_ai_assistant_app. The sample connects a knowledge base and action groups; this guide redraws the design with explicit verification and sponsorship boundaries."),
    "aws-code": ("AWS · Product service source", "https://github.com/aws-solutions-library-samples/guidance-for-generative-ai-shopping-assistant-using-agents-for-amazon-bedrock/blob/main/source/product_service/index.py", "code · load_products / get_product_by_id", "追讀資料來源：S3 products.json 與本機／程序快取。這不是即時庫存一致性的實作。", "Trace S3 products.json and local/process caching. This is not an implementation of real-time inventory consistency."),
    "aws-actions": ("AWS · Shopping action-group handler", "https://github.com/aws-solutions-library-samples/guidance-for-generative-ai-shopping-assistant-using-agents-for-amazon-bedrock/blob/main/deployment/bedrock_agent/shopping_agent/action_groups/create_order_actions/lambda/index.py", "code · tool routing / placeholder actions", "讀 get_product_inventory 與 create_order；有 placeholder，訂單金額也不是完整權威報價流程。", "Inspect get_product_inventory and create_order; some actions are placeholders, and totals do not constitute an authoritative quoting workflow."),
    "aws-schema": ("AWS · Shopping OpenAPI schema", "https://github.com/aws-solutions-library-samples/guidance-for-generative-ai-shopping-assistant-using-agents-for-amazon-bedrock/blob/main/deployment/bedrock_agent/shopping_agent/action_groups/create_order_actions/api_schema/create_order_actions.openapi.json", "code · tool contract", "比較 schema 的 required fields 與實作的驗證，練習設計狀態、錯誤與精確的參數契約。", "Compare required fields with implementation validation; practice explicit status, errors, and precise parameter contracts."),
    "esci": ("Amazon Science · Shopping Queries / ESCI", "https://github.com/amazon-science/esci-data", "2022 · dataset + ranking baselines", "Exact／Substitute／Complement／Irrelevant judgments；產品 metadata、query split、ranking 與 classification baselines。沒有繁體中文或即時 offer 標籤。", "Exact/Substitute/Complement/Irrelevant judgments, product metadata, query splits, and ranking/classification baselines. No Traditional Chinese or live-offer labels."),
    "m2": ("Amazon-M2 · Multilingual Shopping Sessions", "https://arxiv.org/abs/2307.09688", "2023 · original dataset paper", "Session next-product recommendation 與 domain shift。另讀 kddcup23.github.io 的參賽解法；不要把 next-item label 當成購買機率。", "Session next-product recommendation and domain shift. See kddcup23.github.io for competition solutions; next-item labels are not purchase probabilities."),
    "reviews": ("McAuley Lab · Amazon Reviews 2023", "https://amazon-reviews-2023.github.io/", "dataset · reviews / item metadata", "評論、user–item 互動、文字與圖片 metadata；review 時間不代表購買時間，價格欄位也不是即時報價。", "Reviews, user–item interactions, and text/image metadata; review timestamps are not purchase timestamps, and prices are not live quotes."),
    "cosmo": ("Amazon Science · COSMO", "https://www.amazon.science/publications/cosmo-a-large-scale-e-commerce-common-sense-knowledge-generation-and-serving-system-at-amazon", "2024 · original research", "從行為提取用途／意圖知識並過濾、指令微調。可研究候選擴展；不可把意圖推論變成未驗證商品規格。", "Behavior-derived intent/use-case knowledge with filtering and instruction tuning. Useful for candidate expansion, not a substitute for verified product specifications."),
    "contextual": ("Anthropic · Contextual Retrieval", "https://www.anthropic.com/engineering/contextual-retrieval", "2024 · method + experiments", "讀 chunk-specific context、BM25＋dense 與 reranking。原文的實驗效果不代表購物資料必有相同改善。", "Read chunk-specific context, BM25+dense retrieval, and reranking. Published gains do not guarantee the same improvement on shopping data."),
    "cookbook": ("Anthropic · Contextual embeddings notebook", "https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/contextual-embeddings/guide.ipynb", "code · contextual retrieval experiments", "可對照 contextual retrieval 的資料處理與實驗流程；換成自己的商品語料與評估，不直接套用數字。", "Inspect the contextual-retrieval processing and experiment workflow; replace the corpus and evaluation rather than transferring reported numbers."),
    "agents": ("Anthropic · Building Effective Agents", "https://www.anthropic.com/engineering/building-effective-agents", "2024 · workflow / agent patterns", "讀 routing、workflow 與 agent 的取捨；本篇以有界工作流程起步。", "Read routing and workflow/agent tradeoffs; this guide begins with a bounded workflow."),
    "agent-evals": ("Anthropic · Demystifying Evals for AI Agents", "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents", "2026 · evaluation methodology", "Task、trial、grader、trace、outcome；區分最終文字宣稱和環境實際結果。", "Tasks, trials, graders, traces, and outcomes; distinguish final textual claims from actual environment results."),
    "ragchecker": ("Amazon Science · RAGChecker", "https://github.com/amazon-science/RAGChecker", "2024 · paper + evaluation code", "Claim-level 診斷 retrieval／generation；讀 examples/checking_inputs.json 與 metrics。價格／ID 檢查仍應用確定性驗證。", "Claim-level diagnosis of retrieval/generation; inspect examples/checking_inputs.json and metrics. Use deterministic validation for prices and IDs."),
    "tfrs": ("TensorFlow Recommenders · Two-tower retrieval", "https://www.tensorflow.org/recommenders/examples/basic_retrieval", "official tutorial + notebook", "Two-tower、retrieval loss、ANN export；範例是 MovieLens，要重新設計商品資料、negative sampling 與切分。", "Two-tower retrieval, loss, and ANN export. The example uses MovieLens; adapt product data, negative sampling, and splits."),
    "ads": ("Amazon Ads · Sponsored Products / Brands prompts", "https://advertising.amazon.com/resources/whats-new/unboxed-2025-sponsored-products-and-sponsored-brands-prompts", "2026 · product announcement", "公開購物對話與廣告串接的情境；未公開完整 auction／ranking。本文贊助處理是設計建議。", "A public example of ads connected to shopping conversations, not a full auction/ranking disclosure. Sponsorship handling here is a proposed design."),
    "experiments": ("Microsoft Research · Diagnosing Sample Ratio Mismatch", "https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/", "2019 · experimentation research", "用來理解分流與資料品質檢查；解讀效果前先排查 SRM。", "Understand assignment/data-quality checks; investigate SRM before interpreting treatment effects."),
    "interview-source": ("Hello Interview · Recommendation Systems", "https://www.hellointerview.com/learn/ml-system-design/patterns/recommendation-systems", "interview teaching framework", "學 retrieval → ranking → evaluation 的回答順序；這是作者教學方案，不是公司系統證據。", "Learn the retrieval → ranking → evaluation answer structure. This is the author's teaching framework, not evidence of a company's system."),
    "aws-archived": ("AWS · Intelligent shopping assistant", "https://github.com/aws-samples/intelligent-shopping-assistant", "reference code · archived 2026-02-04", "含 data_load_offline、embedding／reranking notebooks、OpenSearch 與 Personalize 整合；已封存，適合讀設計，部署需重新核對相依版本。", "Includes data_load_offline, embedding/reranking notebooks, OpenSearch, and Personalize integration. Archived; useful for design reading, with dependencies requiring revalidation before deployment."),
}


def esc(value):
    return html.escape(str(value), quote=True)


def label(pair):
    assert len(pair) == 2 and all(pair)
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
    parts = []
    if name == "online":
        height = 780
        title = "線上推薦與驗證 / Online recommendation and verification"
        nodes = [
            (400,20,"購物需求與對話狀態","Request + conversation state","navy"),
            (400,116,"意圖、硬限制、必要澄清","Intent / constraints / clarification","white"),
            (60,228,"一般商品檢索","Organic: lexical + dense + session","teal"),
            (740,228,"贊助商品檢索","Sponsored: targeting + eligibility","amber"),
            (400,340,"候選商品／variant／offer IDs","Candidate identities + provenance","white"),
            (400,442,"批次查價、庫存與配送","Live commerce tools + freshness","teal"),
            (400,548,"硬限制驗證、排序與結果組合","Validate → rank → compose slate","white"),
            (60,548,"限定商品與版本的證據檢索","Scoped product / variant evidence","teal"),
            (400,668,"有證據的比較與推薦","Generate supported claims + IDs","white"),
            (740,668,"驗證與結構化渲染","Validate + render trusted fields","navy"),
        ]
        paths = ["M540 86V116", "M540 182V205H200V228", "M540 182V205H880V228", "M200 294V318H510V340", "M880 294V318H570V340", "M540 406V442", "M540 508V548", "M400 581H340", "M200 614V701H400", "M540 614V668", "M680 701H740", "M680 475H880V668"]
        caption = ["圖 1 · 原創重畫。參考 AWS 購物助理與 Rufus 的公開概念；加入商品／證據檢索分工、即時驗證及贊助 provenance。右側直達渲染器的路徑代表可信商務欄位不由生成器改寫。手機可橫向捲動。", "Figure 1 · Original redraw informed by the AWS shopping sample and public Rufus concepts, adding separate product/evidence retrieval, live verification, and sponsorship provenance. The direct renderer path preserves trusted commerce fields outside generation. Scroll horizontally on small screens."]
    else:
        height = 540
        title = "資料與實驗閉環 / Data and experiment loop"
        nodes = [
            (40,30,"商品、規格、來源文件","Catalog / attributes / documents","white"),
            (400,30,"曝光、互動、session 日誌","Exposure / outcome / session logs","white"),
            (760,30,"商務狀態與工具回應","Commerce state + tool results","white"),
            (40,162,"正規化、分塊與版本索引","Normalize → chunk → version index","teal"),
            (400,162,"時間一致的樣本與成熟標籤","Point-in-time examples + maturity","teal"),
            (760,162,"固定快照、時鐘與故障案例","Frozen snapshots + failure fixtures","amber"),
            (400,294,"訓練、ablation、分層評估","Train / ablate / evaluate by layer","white"),
            (400,426,"相容版本發布、觀測與回饋","Versioned release + observe + learn","navy"),
        ]
        paths = ["M180 96V162", "M540 96V162", "M900 96V162", "M180 228V270H490V294", "M540 228V294", "M900 228V270H590V294", "M540 360V426", "M400 459H20V260H180V228"]
        caption = ["圖 2 · 原創資料閉環。索引更新、學習標籤與工具測試保留不同時間語意；發布 encoder／index／ranker／prompt／policy 的相容 bundle，再由線上觀測啟動下一輪診斷。", "Figure 2 · Original data loop. Index updates, learning labels, and tool fixtures preserve distinct time semantics. Release a compatible encoder/index/ranker/prompt/policy bundle, then use online observations for the next diagnostic cycle."]
    parts.append(f'<figure class="diagram"><div class="diagram-scroll" tabindex="0" role="region" aria-label="{esc(title)}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 {height}" role="img" aria-labelledby="diagram-title-{name}"><title id="diagram-title-{name}">{esc(title)}</title><defs><marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#55766a"/></marker></defs>')
    parts.extend(f'<path d="{path}" fill="none" stroke="#55766a" stroke-width="2" stroke-linejoin="round" marker-end="url(#arrow-{name})"/>' for path in paths)
    parts.extend(node(*args) for args in nodes)
    parts.append('</svg></div><figcaption>' + label(caption) + '</figcaption></figure>')
    return "".join(parts)


def render_scenarios(scenarios):
    h = ['<div class="block"><div class="scenario-buttons" role="group" aria-label="Scenario selector">']
    for s in scenarios:
        h.append(f'<button type="button" data-scenario-button="{s["id"]}" aria-controls="scenario-{s["id"]}" aria-pressed="false">{label(s["title"])}</button>')
    h.append('</div>')
    for s in scenarios:
        h.append(f'<section class="scenario-panel" id="scenario-{s["id"]}" data-scenario-panel="{s["id"]}" aria-labelledby="scenario-title-{s["id"]}"><h3 id="scenario-title-{s["id"]}">{label(s["title"])}</h3>')
        for key, heading in (("facts",["觀察到的資料","OBSERVED INPUT"]),("decision",["系統應採取的決策","EXPECTED DECISION"])):
            h.append(f'<div class="scenario-row"><div class="scenario-label">{label(heading)}</div>{pair_text(s[key])}</div>')
        h.append(pair_text(s["check"], "scenario-check") + '</section>')
    h.append('</div>')
    return "".join(h)


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
    sections = data["sections"]
    assert len(sections) == 14 and len({s["id"] for s in sections}) == 14
    nav, options, body = [], [], []
    for n, s in enumerate(sections, 1):
        nav.append(f'<a href="#{s["id"]}"><span class="nav-no">{n:02}</span>{label(s["title"])}</a>')
        options.append(f'<option value="{s["id"]}" data-zh="{esc(s["title"][0])}" data-en="{esc(s["title"][1])}">{esc(s["title"][0])}</option>')
        body.append(f'<section class="section" id="{s["id"]}"><div class="section-kicker">{n:02} / {s["id"].upper()}</div><h2>{label(s["title"])}</h2>{pair_text(s["lead"], "lede")}')
        body.extend(render_block(b, data["scenarios"]) for b in s["blocks"])
        body.append('<div class="section-refs">' + label(["概念／程式來源", "Concept / code sources"]))
        for ref in s["refs"]:
            assert ref in SOURCES
            body.append(f'<a href="#ref-{ref}">{esc(ref.upper())}</a>')
        body.append('</div></section>')
    refs = ['<section class="section" id="sources"><div class="section-kicker">15 / READING & CODE</div><h2>' + label(["來源與程式碼導讀", "Sources and code reading"]) + '</h2>' + pair_text(["以下區分原始研究、官方範例與教學框架。文章支援概念，範例支援介面理解；本篇的整合架構、門檻與實驗設計屬於建議。外部連結需網路；本文與圖表可離線閱讀。", "The list distinguishes original research, official samples, and teaching frameworks. Articles support concepts; samples illustrate interfaces. The integrated architecture, thresholds, and experiments are proposed designs. External links require a network; the guide and diagrams work offline."], "lede") + '<ol class="source-list">']
    for key, (title, url, kind, zh, en) in SOURCES.items():
        refs.append(f'<li id="ref-{key}"><a class="source-title" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(title)} ↗</a><div class="source-meta">{esc(kind)}</div>{pair_text([zh,en])}</li>')
    refs.append('</ol></section>')
    output = (ASSETS / "template.html").read_text(encoding="utf-8")
    output = re.sub(r"\{\{([^{}]+?)\|\|([^{}]+?)\}\}", lambda m: label([m[1].strip(),m[2].strip()]), output)
    for key, value in (("NAV",nav),("OPTIONS",options),("SECTIONS",body),("SOURCES",refs)):
        output = output.replace(f"<!--{key}-->", "\n".join(value))
    assert not re.search(r"job\s+description|\bJD\b|position\s+name|職缺|職稱", output, re.I)
    assert not re.search(r"<!--(?:NAV|OPTIONS|SECTIONS|SOURCES)-->|\{\{", output)
    DEST.write_text(output, encoding="utf-8", newline="\n")
    print(f"Built {DEST.name}: {len(sections)} chapters, {len(SOURCES)} sources, {len(output.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    build()
