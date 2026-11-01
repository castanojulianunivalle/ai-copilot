"""Convierte los .md de los guiones de grabación en PDF usando Chrome/Edge headless.

Uso:
    python _md_to_pdf.py            # convierte los 8 archivos
    python _md_to_pdf.py --dry-run  # solo lista lo que haría
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent

MD_FILES = [
    ROOT / "01_sandra" / "entrevistador.md",
    ROOT / "01_sandra" / "entrevistada.md",
    ROOT / "02_daniela" / "entrevistador.md",
    ROOT / "02_daniela" / "entrevistada.md",
    ROOT / "03_karen" / "entrevistador.md",
    ROOT / "03_karen" / "entrevistada.md",
    ROOT / "04_lina" / "entrevistador.md",
    ROOT / "04_lina" / "entrevistada.md",
]

CSS = """
@page { size: Letter; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #1c1f24;
    max-width: 100%;
}
h1 { font-size: 19pt; margin: 0 0 8pt; color: #0b3d91; border-bottom: 2px solid #0b3d91; padding-bottom: 6pt; }
h2 { font-size: 14pt; margin: 14pt 0 6pt; color: #0b3d91; border-bottom: 1px solid #d0d7de; padding-bottom: 3pt; }
h3 { font-size: 12pt; margin: 12pt 0 4pt; color: #2c3a55; }
h4 { font-size: 11pt; margin: 10pt 0 3pt; color: #2c3a55; }
p, li { margin: 4pt 0; }
ul, ol { padding-left: 18pt; margin: 4pt 0; }
blockquote {
    border-left: 4px solid #0b3d91;
    padding: 4pt 10pt;
    margin: 6pt 0;
    background: #f4f7fb;
    color: #2c3a55;
    font-style: normal;
}
blockquote p { margin: 2pt 0; }
code {
    font-family: "Consolas", "Courier New", monospace;
    background: #f0f3f7;
    padding: 1pt 4pt;
    border-radius: 3pt;
    font-size: 9.5pt;
}
pre {
    background: #1f2937;
    color: #f9fafb;
    padding: 8pt 10pt;
    border-radius: 4pt;
    overflow-x: auto;
    font-size: 9pt;
}
pre code { background: transparent; color: inherit; padding: 0; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 6pt 0;
    font-size: 9.5pt;
}
th, td {
    border: 1px solid #d0d7de;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
}
th { background: #eef2ff; color: #1c2a4a; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 12pt 0; }
strong { color: #1c1f24; }
em { color: #2c3a55; }
a { color: #0b3d91; text-decoration: none; }
.emoji { font-size: 11pt; }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""


def find_chrome() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    raise FileNotFoundError("No se encontró Chrome ni Edge en rutas estándar.")


def md_to_html(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "nl2br", "sane_lists"],
        output_format="html5",
    )
    return HTML_TEMPLATE.format(title=md_path.stem, css=CSS, body=html_body)


def html_to_pdf(html_text: str, pdf_path: Path, browser: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(html_text)
        html_tmp = Path(tmp.name)

    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_tmp.as_uri(),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Chrome/Edge devolvió código {result.returncode}: {result.stderr}"
            )
    finally:
        try:
            html_tmp.unlink()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true", help="Listar sin convertir"
    )
    args = parser.parse_args()

    browser = find_chrome()
    print(f"Usando navegador: {browser}\n")

    missing = [p for p in MD_FILES if not p.exists()]
    if missing:
        print("ERROR · Archivos faltantes:")
        for p in missing:
            print(f"  - {p}")
        return 1

    for md_path in MD_FILES:
        pdf_path = md_path.with_suffix(".pdf")
        rel = md_path.relative_to(ROOT)
        if args.dry_run:
            print(f"[DRY-RUN] {rel} -> {pdf_path.name}")
            continue
        print(f"Convirtiendo {rel} ... ", end="", flush=True)
        html_text = md_to_html(md_path)
        html_to_pdf(html_text, pdf_path, browser)
        size_kb = pdf_path.stat().st_size / 1024
        print(f"OK ({size_kb:.1f} KB)")

    print("\nListo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
