"""Combina todos los documentos finales de UX Research en un único PDF.

Estructura del PDF resultante:
    1. Portada
    2. Aviso de videos (con enlaces a Drive)
    3. Índice
    4. Resumen (README)
    5. Guía de entrevista
    6. Consentimiento informado
    7. 4 transcripciones de entrevistas
    8. Diagrama de afinidad
    9. User Personas
   10. User Story Mapping
   11. Guion del video del USM

Uso:
    python _build_combined_pdf.py
    python _build_combined_pdf.py --output Otro_Nombre.pdf
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "Investigacion_UX_completa.pdf"

# Orden en que se concatenan los documentos en el entregable.
# El guion del video del USM (10_guion_video_usm.md) NO se incluye porque
# es material de preparación; el docente recibe el video, no el guion.
SECTIONS: list[tuple[str, Path]] = [
    ("Resumen del trabajo",          ROOT / "README.md"),
    ("Guía de entrevista",           ROOT / "anexos" / "02_guia_entrevista.md"),
    ("Consentimiento informado",     ROOT / "anexos" / "01_consentimiento_informado.md"),
    ("Entrevista 01 — Sandra Liliana M. (Clienta Novata)",
        ROOT / "entrevistas" / "03_entrevista_01_cliente_novato.md"),
    ("Entrevista 02 — Daniela Andrea R. (Clienta Avanzada)",
        ROOT / "entrevistas" / "04_entrevista_02_cliente_avanzado.md"),
    ("Entrevista 03 — Karen Vanessa G. (Agente de Soporte)",
        ROOT / "entrevistas" / "05_entrevista_03_agente_soporte.md"),
    ("Entrevista 04 — Lina Marcela Q. (Coordinadora)",
        ROOT / "entrevistas" / "06_entrevista_04_coordinador_admin.md"),
    ("Diagrama de Afinidad",         ROOT / "diagrama_afinidad" / "07_diagrama_afinidad.md"),
    ("User Personas",                ROOT / "08_user_personas.md"),
    ("User Story Mapping",           ROOT / "09_user_story_mapping.md"),
]

CSS = """
@page { size: Letter; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #1c1f24;
}
h1 { font-size: 18pt; margin: 0 0 8pt; color: #0b3d91; border-bottom: 2px solid #0b3d91; padding-bottom: 6pt; }
h2 { font-size: 13pt; margin: 14pt 0 6pt; color: #0b3d91; border-bottom: 1px solid #d0d7de; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; color: #2c3a55; }
h4 { font-size: 10.5pt; margin: 10pt 0 3pt; color: #2c3a55; }
p, li { margin: 4pt 0; }
ul, ol { padding-left: 18pt; margin: 4pt 0; }
blockquote {
    border-left: 4px solid #0b3d91;
    padding: 4pt 10pt;
    margin: 6pt 0;
    background: #f4f7fb;
    color: #2c3a55;
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
    white-space: pre-wrap;
    word-wrap: break-word;
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

/* Page-break helpers */
.page-break { page-break-before: always; }
.section { page-break-before: always; }
.section:first-child { page-break-before: auto; }

/* Cover */
.cover {
    height: 240mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    page-break-after: always;
}
.cover .eyebrow {
    font-size: 11pt;
    letter-spacing: 4pt;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 12pt;
}
.cover .title {
    font-size: 30pt;
    font-weight: 700;
    color: #0b3d91;
    margin: 0 0 8pt;
    line-height: 1.15;
}
.cover .subtitle {
    font-size: 16pt;
    color: #2c3a55;
    margin: 0 0 28pt;
}
.cover .meta {
    font-size: 11pt;
    color: #1c1f24;
    margin: 4pt 0;
}
.cover .meta strong { color: #0b3d91; }
.cover .footer {
    margin-top: 36pt;
    font-size: 9.5pt;
    color: #6b7280;
}

/* TOC */
.toc h1 { margin-bottom: 14pt; }
.toc ol { font-size: 11pt; line-height: 1.8; }
.toc ol li { color: #1c1f24; }

/* Section header */
.section-title-card {
    background: #f4f7fb;
    border-left: 6px solid #0b3d91;
    padding: 14pt 18pt;
    margin-bottom: 14pt;
}
.section-title-card .step {
    font-size: 9pt;
    letter-spacing: 3pt;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 4pt;
}
.section-title-card h1 {
    border: none;
    padding: 0;
    margin: 0;
    font-size: 22pt;
    color: #0b3d91;
}

/* Drive notice */
.drive-notice {
    background: #fff7ed;
    border: 1px solid #fdba74;
    border-radius: 6pt;
    padding: 12pt 16pt;
    margin: 12pt 0;
}
.drive-notice strong { color: #9a3412; }
"""

HTML_HEAD = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Investigación UX — Mesa de Ayuda · Support Co-Pilot</title>
<style>{css}</style>
</head>
<body>
"""

HTML_TAIL = "</body></html>"

COVER_HTML = """
<section class="cover">
    <div class="eyebrow">Investigación UX</div>
    <h1 class="title">Mesa de Ayuda<br>AI Support Co-Pilot</h1>
    <div class="subtitle">Diseño Centrado en el Usuario aplicado al dominio</div>
    <div class="meta"><strong>Estudiante:</strong> Julian Castaño</div>
    <div class="meta">castano.julian@correounivalle.edu.co</div>
    <div class="meta"><strong>Programa:</strong> Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes (CODING)</div>
    <div class="meta"><strong>Fecha:</strong> mayo de 2026</div>
    <div class="footer">
        Documento integrado · 11 secciones · Material complementario en Drive
    </div>
</section>
"""

DRIVE_NOTICE_HTML = """
<section class="section">
    <div class="section-title-card">
        <div class="step">Anexo · Material adjunto</div>
        <h1>Videos de entrevistas y video del USM</h1>
    </div>

    <div class="drive-notice">
        <strong>Aviso importante:</strong> los videos de las cuatro entrevistas de UX
        y el video explicativo del User Story Mapping <strong>no están embebidos en este PDF</strong>
        debido a su tamaño. Se entregan como enlaces a una carpeta privada de Google Drive.
        Solicitar acceso al correo del estudiante si el enlace no abre.
    </div>

    <h2>Tabla de enlaces</h2>

    <table>
        <thead>
            <tr>
                <th>Pieza</th>
                <th>Duración</th>
                <th>Enlace de Drive</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Video Entrevista 1 — Sandra L. (Clienta Novata)</td>
                <td>~10 min</td>
                <td><em>[pegar enlace de Drive antes de la entrega]</em></td>
            </tr>
            <tr>
                <td>Video Entrevista 2 — Daniela R. (Clienta Avanzada)</td>
                <td>~10 min</td>
                <td><em>[pegar enlace de Drive antes de la entrega]</em></td>
            </tr>
            <tr>
                <td>Video Entrevista 3 — Karen G. (Agente de Soporte)</td>
                <td>~10 min</td>
                <td><em>[pegar enlace de Drive antes de la entrega]</em></td>
            </tr>
            <tr>
                <td>Video Entrevista 4 — Lina Q. (Coordinadora)</td>
                <td>~10 min</td>
                <td><em>[pegar enlace de Drive antes de la entrega]</em></td>
            </tr>
            <tr>
                <td>Video explicativo del User Story Mapping</td>
                <td>~8-10 min</td>
                <td><em>[pegar enlace de Drive antes de la entrega]</em></td>
            </tr>
            <tr>
                <td>Carpeta general (consentimientos firmados + videos)</td>
                <td>—</td>
                <td><em>[pegar enlace de Drive de la carpeta raíz]</em></td>
            </tr>
        </tbody>
    </table>

    <h2>Notas sobre los videos</h2>

    <ul>
        <li>Cada video corresponde a una entrevista de aproximadamente <strong>10 minutos</strong>
            siguiendo la guía descrita en la sección «Guía de entrevista» de este documento.</li>
        <li>Las grabaciones cuentan con <strong>consentimiento informado firmado</strong>;
            los PDFs firmados se conservan en la misma carpeta de Drive.</li>
        <li>El video del USM tiene una duración objetivo de 8 a 10 minutos y sigue el
            storyboard descrito en la última sección de este documento.</li>
        <li>Las identidades de las entrevistadas se anonimizan en este documento
            mediante pseudónimos. Los videos sin anonimizar son evidencia académica
            de uso restringido.</li>
    </ul>
</section>
"""


def build_toc(sections: list[tuple[str, Path]]) -> str:
    items = "\n".join(
        f"            <li>{title}</li>" for title, _ in sections
    )
    return f"""
<section class="section toc">
    <div class="section-title-card">
        <div class="step">Índice</div>
        <h1>Contenido del documento</h1>
    </div>

    <ol>
        <li>Anexo · Material adjunto: videos en Drive</li>
{items}
    </ol>
</section>
"""


def _strip_section(text: str, header: str) -> str:
    """Elimina la sección que arranca con `header` (un H2) hasta el siguiente H2 o EOF."""
    pattern = rf"{re.escape(header)}.*?(?=\n## |\Z)"
    return re.sub(pattern, "", text, flags=re.DOTALL)


def preprocess_readme(text: str) -> str:
    """Quita del README las secciones de uso interno (estructura de carpetas,
    flujo de producción, guía de lectura) y la tabla de evidencias en video
    —que ya aparece como anexo al inicio del PDF—. Renumera lo que queda."""
    for header in (
        "## 3. Estructura de la carpeta",
        "## 5. Evidencias en video",
        "## 7. Cómo leer este material",
        "## 8. Flujo cronológico recomendado",
    ):
        text = _strip_section(text, header)

    text = text.replace("## 4. Muestra", "## 3. Muestra")
    text = text.replace("## 6. Trazabilidad", "## 4. Trazabilidad")

    # En la tabla de "Puntos resueltos", reemplaza la referencia al guion del video
    # (que ya no se entrega como documento) por una nota al video adjunto en Drive.
    text = text.replace(
        ", [`10_guion_video_usm.md`](./10_guion_video_usm.md)",
        " (video adjunto en Drive)",
    )

    # Limpia el bloque de Programa/correo/proyecto base: el correo y la maestría
    # ya están en la portada; mantenerlos repite información.
    text = re.sub(
        r"^> Programa:.*?\n> Estudiante:.*?\n> Proyecto base:.*?\n",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    return text


def preprocess_general(text: str) -> str:
    """Filtros aplicables a cualquier documento."""
    # Elimina referencias a imágenes placeholder cuyos archivos no existen
    text = re.sub(r"!\[placeholder.*?\]\([^)]+\)\s*\n?", "", text)
    # Elimina líneas '📷 Evidencia fotográfica ...' que apuntan a capturas no adjuntas
    text = re.sub(r"^📷.*$\n?", "", text, flags=re.MULTILINE)
    # Elimina referencias internas a 10_guion_video_usm.md
    text = re.sub(
        r"\(?\[`?10_guion_video_usm\.md`?\]\([^)]+\)\)?",
        "(video adjunto en Drive)",
        text,
    )
    return text


def md_to_html_body(md_path: Path) -> str:
    """Convierte el cuerpo del MD a HTML aplicando los filtros de entrega."""
    text = md_path.read_text(encoding="utf-8")
    text = preprocess_general(text)
    if md_path.name == "README.md":
        text = preprocess_readme(text)
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        output_format="html5",
    )


def section_html(step: int, title: str, md_path: Path) -> str:
    body = md_to_html_body(md_path)
    # Si el primer elemento es un h1, lo reemplazamos por nuestra tarjeta de sección
    body = re.sub(
        r"^\s*<h1>.*?</h1>",
        "",
        body,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return f"""
<section class="section">
    <div class="section-title-card">
        <div class="step">Sección {step}</div>
        <h1>{title}</h1>
    </div>
    {body}
</section>
"""


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


def html_to_pdf(html_text: str, pdf_path: Path, browser: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(html_text)
        html_tmp = Path(tmp.name)
    profile_dir = Path(tempfile.mkdtemp(prefix="chrome-pdf-"))
    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={pdf_path}",
            html_tmp.as_uri(),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
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
        try:
            import shutil
            shutil.rmtree(profile_dir, ignore_errors=True)
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Ruta del PDF de salida",
    )
    args = parser.parse_args()

    missing = [p for _, p in SECTIONS if not p.exists()]
    if missing:
        print("ERROR · Archivos faltantes:")
        for p in missing:
            print(f"  - {p}")
        return 1

    browser = find_chrome()
    print(f"Usando navegador: {browser}\n")

    parts: list[str] = [
        HTML_HEAD.format(css=CSS),
        COVER_HTML,
        DRIVE_NOTICE_HTML,
        build_toc(SECTIONS),
    ]
    for idx, (title, md_path) in enumerate(SECTIONS, start=1):
        rel = md_path.relative_to(ROOT)
        print(f"  + Sección {idx:>2}: {title} ({rel})")
        parts.append(section_html(idx, title, md_path))
    parts.append(HTML_TAIL)

    html_text = "".join(parts)

    print(f"\nGenerando PDF: {args.output.relative_to(ROOT)}")
    html_to_pdf(html_text, args.output, browser)
    size_kb = args.output.stat().st_size / 1024
    print(f"OK ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
