"""Export a local HTML document to PDF with one headless Chrome render.

The HTML owns its print layout through ``@media print`` and ``@page`` CSS.
This exporter has no Python package dependencies and does not use Playwright.

Examples:
    python scripts/export_html_pdf.py
    python scripts/export_html_pdf.py --source summaries/zh-TW/other.html \
        --output pdfs/other.pdf
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "summaries" / "zh-TW" / "build-gpt-ml-practice.html"
DEFAULT_OUTPUT = ROOT / "pdfs" / "build-gpt-ml-practice.pdf"

CHROME_CANDIDATES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
)


def repository_path(value: Path) -> Path:
    """Resolve relative CLI paths from the repository root."""
    value = value.expanduser()
    return (value if value.is_absolute() else ROOT / value).resolve()


def find_chrome(explicit: str | None = None) -> str:
    """Return an installed Chrome or Edge executable."""
    candidates = (explicit,) if explicit else CHROME_CANDIDATES
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.is_file():
            return str(path.resolve())
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise SystemExit("No Chrome or Edge executable found. Use --chrome PATH.")


def render_pdf(chrome: str, source: Path, output: Path, timeout: int) -> float:
    """Render once and atomically replace the requested output PDF."""
    output.parent.mkdir(parents=True, exist_ok=True)

    temporary_handle = tempfile.NamedTemporaryFile(
        dir=output.parent,
        prefix=f".{output.stem}-",
        suffix=".tmp.pdf",
        delete=False,
    )
    temporary_output = Path(temporary_handle.name)
    temporary_handle.close()
    temporary_output.unlink()

    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix="html-pdf-chrome-") as profile:
            try:
                result = subprocess.run(
                    [
                        chrome,
                        "--headless=new",
                        "--disable-gpu",
                        "--disable-extensions",
                        "--no-first-run",
                        "--no-default-browser-check",
                        f"--user-data-dir={profile}",
                        "--no-pdf-header-footer",
                        f"--print-to-pdf={temporary_output}",
                        source.as_uri(),
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                )
            except subprocess.TimeoutExpired as exc:
                raise SystemExit(
                    f"Chrome PDF rendering timed out after {timeout} seconds."
                ) from exc

        if result.returncode != 0:
            raise SystemExit(f"Chrome PDF rendering failed:\n{result.stderr}")
        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise SystemExit("Chrome completed without producing a PDF.")
        if temporary_output.read_bytes()[:5] != b"%PDF-":
            raise SystemExit("Chrome output does not have a valid PDF header.")

        os.replace(temporary_output, output)
    finally:
        temporary_output.unlink(missing_ok=True)

    return time.perf_counter() - started


def read_pdf_info(output: Path) -> dict[str, str]:
    """Read basic PDF metadata when Poppler's pdfinfo is available."""
    executable = shutil.which("pdfinfo")
    if not executable:
        return {}

    result = subprocess.run(
        [executable, str(output)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if result.returncode != 0:
        raise SystemExit(f"pdfinfo could not validate the generated PDF:\n{result.stderr}")

    info: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            info[key.strip()] = value.strip()
    return info


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--chrome", help="Chrome or Edge executable path")
    parser.add_argument("--timeout", type=int, default=60, help="Render timeout in seconds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = repository_path(args.source)
    output = repository_path(args.output)

    if not source.is_file():
        raise SystemExit(f"Source HTML does not exist: {source}")
    if source == output:
        raise SystemExit("Source HTML and output PDF must be different files.")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be greater than zero.")

    chrome = find_chrome(args.chrome)
    elapsed = render_pdf(chrome, source, output, args.timeout)
    info = read_pdf_info(output)

    details = [f"{output.stat().st_size:,} bytes", f"{elapsed:.2f}s"]
    if pages := info.get("Pages"):
        details.insert(0, f"{pages} pages")
    if page_size := info.get("Page size"):
        details.append(page_size)

    print(f"Wrote {output}")
    print(" | ".join(details))
    return 0


if __name__ == "__main__":
    sys.exit(main())
