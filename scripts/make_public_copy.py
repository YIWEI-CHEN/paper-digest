"""Create public copies of the SLiCE schema-lineage digests without the
private Section 08 (interview prep) and Section 09 (code map) blocks."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "summaries"

TARGETS = [
    (BASE / "zh-TW" / "slice-schema-lineage-zhtw.html",
     BASE / "zh-TW" / "slice-schema-lineage-zhtw-public.html"),
    (BASE / "en" / "slice-schema-lineage-en.html",
     BASE / "en" / "slice-schema-lineage-en-public.html"),
]

DROP_IDS = ("interview", "code")


def strip_sections(lines):
    out, skip = [], None
    for line in lines:
        if skip is None:
            m = re.match(r'\s*<section id="([^"]+)">', line)
            if m and m.group(1) in DROP_IDS:
                skip = m.group(1)
                continue
            # TOC links pointing at the dropped sections
            if re.search(r'<a href="#(%s)">' % "|".join(DROP_IDS), line):
                continue
            out.append(line)
        else:
            if line.strip() == "</section>":
                skip = None
    return out


def strip_footer_note(text):
    # Remove the trailing sentence that references sections 08/09.
    text = re.sub(r"<br>\s*Sections 08 and 09 are interview-preparation additions[^<]*", "", text)
    text = re.sub(r"<br>\s*Section 08 為面試準備補充[^<]*", "", text)
    return text


for src, dst in TARGETS:
    lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = strip_sections(lines)
    text = strip_footer_note("".join(kept))
    # Collapse the blank line left where a section was removed.
    text = re.sub(r"\n{3,}", "\n\n", text)
    dst.write_text(text, encoding="utf-8")
    print(f"{src.name} -> {dst.name}: {len(lines)} -> {len(text.splitlines())} lines")
