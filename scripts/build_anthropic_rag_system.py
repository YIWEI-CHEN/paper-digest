"""Build the bilingual, offline-readable RAG system design guide (stdlib only)."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/anthropic-rag-system-deep-dive"
DEST = ROOT / "summaries/zh-TW/anthropic-rag-system-deep-dive.html"


def esc(value):
    return html.escape(str(value), quote=True)


def label(value):
    assert isinstance(value, list) and len(value) == 2 and all(value), value
    return f'<span class="label"><span class="zh" lang="zh-Hant">{esc(value[0])}</span><span class="en" lang="en">{esc(value[1])}</span></span>'


def pair(value, extra=""):
    assert isinstance(value, list) and len(value) == 2 and all(value), value
    return f'<div class="pair {extra}"><p class="zh" lang="zh-Hant">{esc(value[0])}</p><p class="en" lang="en">{esc(value[1])}</p></div>'


def node(x, y, zh, en, tone="white", width=280):
    fills = {"white": "#ffffff", "blue": "#e4edf9", "amber": "#fff1d8", "navy": "#203a5c"}
    color = "#f6fafc" if tone == "navy" else "#203a5c"
    return (f'<rect x="{x}" y="{y}" width="{width}" height="66" rx="8" fill="{fills[tone]}" stroke="#aebed3"/>'
            f'<text class="zh" lang="zh-Hant" x="{x+width/2}" y="{y+27}" fill="{color}" text-anchor="middle" font-size="15" font-weight="600">{esc(zh)}</text>'
            f'<text class="en" lang="en" x="{x+width/2}" y="{y+47}" fill="{color}" text-anchor="middle" font-size="12">{esc(en)}</text>')


def diagram(name):
    if name == "online":
        height, title = 796, "授權範圍內的證據路徑 / An authorized evidence path"
        nodes = [
            (400,20,"問題、對話與可信身分","Query / conversation / identity","navy"),
            (400,122,"解析版本、時間與授權範圍","Resolve scope + current permissions","white"),
            (60,224,"詞彙檢索與精確識別碼","BM25 + exact identifiers","blue"),
            (740,224,"語意檢索與相容向量索引","Dense retrieval + compatible index","blue"),
            (400,326,"合併、去重與候選精排","Fuse → deduplicate → rerank","white"),
            (400,428,"取原文、驗版本與目前權限","Fetch evidence + recheck access","blue"),
            (400,530,"涵蓋問題、例外與矛盾","Pack evidence + assess sufficiency","white"),
            (60,530,"有界補查、澄清或部分回答","Bounded search / clarify / abstain","amber"),
            (400,632,"依證據生成答案與引用","Generate with source citations","white"),
            (740,632,"驗引用、主張與適用性","Validate pointers / claims / scope","navy"),
        ]
        paths = ["M540 86V122","M540 188V205H200V224","M540 188V205H880V224","M200 290V309H510V326","M880 290V309H570V326","M540 392V428","M540 494V530","M400 563H340","M60 563H20V155H400","M540 596V632","M680 665H740"]
        notes = [(540,742,"檢索失敗、無權限與無答案分開記錄","Trace retrieval failure, access limits, and missing evidence separately")]
        caption = ["圖 1 · 原創重畫：借鏡公開 retrieval／reranking 與 workflow 概念。兩種檢索都在可信授權範圍內；補查有次數與 deadline 上限。圖中驗證可偵測問題，不能保證語意永遠正確。", "Figure 1 · Original redraw informed by public retrieval/reranking and workflow concepts. Both retrievers enforce trusted access scope; retries have call and deadline limits. Validation detects failures but cannot guarantee semantic correctness."]
    elif name == "ingestion":
        height, title = 658, "文件更新與證據血緣 / Updates and evidence provenance"
        nodes = [
            (400,20,"文件新增、修改、刪除與撤權","Document changes + access revocation","navy"),
            (400,132,"解析結構、版本與原始位置","Parse structure / versions / source spans","white"),
            (60,244,"不可變的原始證據快照","Immutable source evidence snapshots","blue"),
            (740,244,"切塊與可選的上下文生成","Chunk + optional contextualization","amber"),
            (400,356,"原文與衍生表示分開儲存","Raw evidence ≠ derived retrieval text","white"),
            (60,468,"BM25 與向量索引相容發布","Publish compatible lexical + vector indexes","blue"),
            (740,468,"Tombstone、權限與快取失效","Tombstones / ACL / cache invalidation","amber"),
        ]
        paths = ["M540 86V132","M540 198V222H200V244","M540 198V222H880V244","M200 310V336H500V356","M880 310V336H580V356","M540 422V444H200V468","M680 53H1045V501H1020"]
        notes = [(540,587,"索引回滾不能恢復已撤銷的權限或已刪除的內容","Rolling back an index must never restore revoked access or deleted content")]
        caption = ["圖 2 · 原創重畫。參考 Contextual Retrieval 的離線處理方式，增加來源版本、衍生文字血緣與獨立失效路徑。原始證據是引用依據；衍生 context 是檢索表示，兩者不能混為一談。", "Figure 2 · Original redraw of the offline processing concept, extended with source versions, derived-text provenance, and a separate invalidation path. Original evidence supports citations; generated context is a retrieval representation."]
    elif name == "diagnosis":
        height, title = 540, "用受控實驗定位錯誤 / Controlled diagnostic experiments"
        nodes = [
            (400,20,"固定問題、語料、權限與預算","Freeze questions / corpus / access / budget","navy"),
            (40,154,"Gold evidence → 同一生成器","Oracle evidence → same generator","blue"),
            (400,154,"固定候選 → 更換 reranker","Fixed candidates → compare rerankers","blue"),
            (760,154,"固定證據 → 更換生成設定","Fixed evidence → compare generation","blue"),
            (40,288,"完整證據下仍有的回答錯誤","Residual errors with sufficient evidence","white"),
            (400,288,"排序與必要證據保留差異","Ranking + evidence-retention changes","white"),
            (760,288,"主張支持、完整性與成本差異","Support / completeness / cost changes","white"),
            (400,422,"配對分析、人工校準與線上驗證","Paired analysis → human check → online","navy"),
        ]
        paths = ["M540 86V120H180V154","M540 86V154","M540 86V120H900V154","M180 220V288","M540 220V288","M900 220V288","M180 354V391H500V422","M540 354V422","M900 354V391H580V422"]
        notes = []
        caption = ["圖 3 · 原創診斷圖，參考 RAGChecker 的分層觀點與公開 eval 方法。一次固定其他變因，才能分辨資料、候選、排序、context packing 和生成器的貢獻。Gold evidence 的人工完整性也要審查。", "Figure 3 · Original diagnostic design informed by layered RAG evaluation. Hold other variables fixed to isolate ingestion, candidate retrieval, ranking, packing, and generation. Human review must also check whether oracle evidence is complete."]
    else:
        raise ValueError(name)
    h = [f'<figure class="diagram"><div class="diagram-scroll" tabindex="0" role="region" aria-label="{esc(title)}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 {height}" role="img" aria-labelledby="diagram-title-{name}"><title id="diagram-title-{name}">{esc(title)}</title><defs><marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#627d9c"/></marker></defs>']
    h.extend(f'<path d="{p}" fill="none" stroke="#627d9c" stroke-width="2" stroke-linejoin="round" marker-end="url(#arrow-{name})"/>' for p in paths)
    h.extend(node(*n) for n in nodes)
    for x,y,zh,en in notes:
        h.append(f'<text class="zh" x="{x}" y="{y}" text-anchor="middle" font-size="14" fill="#526781">{esc(zh)}</text><text class="en" x="{x}" y="{y+20}" text-anchor="middle" font-size="12" fill="#526781">{esc(en)}</text>')
    return ''.join(h) + '</svg></div><figcaption>' + label(caption) + '</figcaption></figure>'


def scenarios(items):
    h = ['<div class="block"><div class="scenario-buttons" role="group" aria-label="Scenario selector">']
    for s in items:
        h.append(f'<button type="button" data-scenario-button="{s["id"]}" aria-controls="scenario-{s["id"]}" aria-pressed="false">{label(s["title"])}</button>')
    h.append('</div>')
    for s in items:
        h.append(f'<section class="scenario-panel" id="scenario-{s["id"]}" data-scenario-panel="{s["id"]}" aria-labelledby="scenario-title-{s["id"]}"><h3 id="scenario-title-{s["id"]}">{label(s["title"])}</h3>')
        for key,title in (("facts",["觀察到的資料","OBSERVED INPUT"]),("decision",["系統應採取的決策","EXPECTED DECISION"])):
            h.append('<div class="scenario-row"><div class="scenario-label">' + label(title) + '</div>' + pair(s[key]) + '</div>')
        h.append(pair(s['check'], 'scenario-check') + '</section>')
    return ''.join(h) + '</div>'


def block(b, items):
    t = b['type']
    if t == 'p': return pair(b['text'], 'block')
    if t == 'callout': return '<div class="callout block"><h3>' + label(b['title']) + '</h3>' + pair(b['text']) + '</div>'
    if t == 'cards': return '<div class="cards block">' + ''.join('<div class="card"><h3>' + label(c['title']) + '</h3>' + pair(c['text']) + '</div>' for c in b['items']) + '</div>'
    if t == 'table':
        assert all(len(r) == len(b['headers']) for r in b['rows'])
        return '<div class="table-wrap block" tabindex="0" role="region" aria-label="Comparison table"><table><thead><tr>' + ''.join('<th scope="col">' + label(v) + '</th>' for v in b['headers']) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + label(v) + '</td>' for v in row) + '</tr>' for row in b['rows']) + '</tbody></table></div>'
    if t == 'formula': return '<pre class="formula block"><code>' + esc(b['text']) + '</code></pre>'
    if t == 'code': return '<div class="block"><div class="code-caption">' + label(b['caption']) + '</div><pre><code>' + esc(b['code']) + '</code></pre></div>'
    if t == 'qa': return '<details class="followup"><summary>' + label(b['q']) + '</summary>' + pair(b['a']) + '</details>'
    if t == 'diagram': return diagram(b['name'])
    if t == 'scenarios': return scenarios(items)
    raise ValueError(t)


def build():
    data = json.loads((ASSETS / 'content.json').read_text(encoding='utf-8'))
    sections, sources = data['sections'], {s['id']:s for s in data['sources']}
    assert len(sections) == len({s['id'] for s in sections}) == 14
    assert len(data['scenarios']) == len({s['id'] for s in data['scenarios']}) == 6
    assert len(sources) == len(data['sources'])
    nav, options, body = [], [], []
    for n,s in enumerate(sections,1):
        nav.append(f'<a href="#{s["id"]}"><span class="nav-no">{n:02}</span>{label(s["title"])}</a>')
        options.append(f'<option value="{s["id"]}" data-zh="{esc(s["title"][0])}" data-en="{esc(s["title"][1])}">{esc(s["title"][0])}</option>')
        body.append(f'<section class="section" id="{s["id"]}"><div class="section-kicker">{n:02} / {s["id"].upper()}</div><h2>{label(s["title"])}</h2>{pair(s["lead"],"lede")}')
        body.extend(block(b,data['scenarios']) for b in s['blocks'])
        body.append('<div class="section-refs">' + label(["概念／程式來源","Concept / code sources"]))
        for ref in s['refs']:
            assert ref in sources, ref
            body.append(f'<a href="#ref-{ref}">{esc(ref.upper())}</a>')
        body.append('</div></section>')
    refs = ['<section class="section" id="sources"><div class="section-kicker">15 / RESEARCH & CODE</div><h2>' + label(["研究來源與程式碼","Research sources and code"]) + '</h2>' + pair(["來源涵蓋官方文章、API 文件、原始論文與實作。實驗數字屬原作者結果；本篇架構、案例、容量與實驗設計是綜合建議。程式已閱讀，未執行付費 API 或重現作者成績。", "Sources include official articles, API documentation, original papers, and implementation code. Reported results belong to their authors; the architecture, scenarios, capacity estimates, and experiments here are proposed designs. Code was read; paid APIs and published experiments were not run."], 'lede') + '<ol class="source-list">']
    for s in data['sources']:
        assert s['url'].startswith('https://')
        refs.append(f'<li id="ref-{s["id"]}"><a class="source-title" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["title"])} ↗</a><div class="source-meta">{esc(s["kind"])}</div>{pair(s["notes"])}</li>')
    refs.append('</ol></section>')
    output = (ASSETS / 'template.html').read_text(encoding='utf-8')
    output = re.sub(r'\{\{([^{}]+?)\|\|([^{}]+?)\}\}',lambda m:label([m[1].strip(),m[2].strip()]),output)
    for k,v in (("NAV",nav),("OPTIONS",options),("SECTIONS",body),("SOURCES",refs)):
        output = output.replace(f'<!--{k}-->', '\n'.join(v))
    assert not re.search(r'<!--(?:NAV|OPTIONS|SECTIONS|SOURCES)-->|\{\{',output)
    assert not re.search(r'job\s+description|\bJD\b|position\s+name|職缺|職稱',output,re.I)
    assert 'copilot-shopping' not in output and '#shopping' not in output
    DEST.write_text(output,encoding='utf-8',newline='\n')
    print(f'Built {DEST.name}: {len(sections)} chapters, {len(sources)} sources, {len(output.encode("utf-8")):,} bytes')


if __name__ == '__main__':
    build()
