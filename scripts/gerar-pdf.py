#!/usr/bin/env python3
"""Gera PDF e HTML — design premium editorial."""

import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUTO = ROOT / "produto"
ENTREGA = ROOT / "entrega"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500;9..144,600'
    '&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">'
)

MODULE_DATA = {
    "1": ("Ganchos e ideias", "Formatos de abertura, tendências e ideias de conteúdo."),
    "2": ("Roteiros para vídeo", "Estruturas para Reels, TikTok e vídeos curtos."),
    "3": ("Legendas e copy", "Textos para feed, stories, bio e conversão."),
    "4": ("Conteúdo educativo", "Autoridade, FAQ e materiais de valor."),
    "5": ("Vendas e conversão", "Ofertas, follow-up e objeções."),
    "6": ("Organização", "Planejamento e rotina de produção."),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def parse_prompts(md: str) -> list[dict]:
    prompts = []
    for block in re.split(r"(?=### PROMPT \d+)", md):
        m = re.match(r"### PROMPT (\d+) — (.+?)(?:\n|$)", block)
        if not m:
            continue
        num, title = m.group(1), m.group(2).strip()
        quando = re.search(r"\*\*QUANDO USAR:\*\*\s*(.+)", block)
        prompt_m = re.search(r"\*\*PROMPT \(copiar e colar\):\*\*\s*```\n(.*?)```", block, re.S)
        dica = re.search(r"\*\*DICA:\*\*\s*(.+)", block)
        module_num, module_name = "", ""
        for mm in re.finditer(r"# MÓDULO (\d+) — (.+)", md):
            if mm.start() < md.find(block):
                module_num = mm.group(1)
                module_name = mm.group(2).strip().split("(")[0].strip()
        prompts.append({
            "num": num, "title": title,
            "module_num": module_num, "module_name": module_name,
            "quando": quando.group(1).strip() if quando else "",
            "body": prompt_m.group(1).strip() if prompt_m else "",
            "dica": dica.group(1).strip() if dica else "",
        })
    return prompts


def parse_order_bump(md: str) -> list[dict]:
    items = []
    for block in re.split(r"(?=## PROMPT B\d+)", md):
        m = re.match(r"## PROMPT (B\d+) — (.+?)(?:\n|$)", block)
        if not m:
            continue
        quando = re.search(r"\*\*QUANDO USAR:\*\*\s*(.+)", block)
        prompt_m = re.search(r"```\n(.*?)```", block, re.S)
        items.append({
            "num": m.group(1).replace("B", ""),
            "title": m.group(2).strip(),
            "quando": quando.group(1).strip() if quando else "",
            "body": prompt_m.group(1).strip() if prompt_m else "",
        })
    return items


def md_table_to_html(md_chunk: str) -> str:
    rows = []
    for line in md_chunk.strip().splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[-:\s|]+\|$", line):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    if not rows:
        return ""
    out = '<div class="table-wrap"><table>'
    for i, row in enumerate(rows):
        tag = "th" if i == 0 else "td"
        out += "<tr>" + "".join(f"<{tag}>{html_escape(c)}</{tag}>" for c in row) + "</tr>"
    return out + "</table></div>"


def render_calendar(md: str) -> str:
    html = ""
    for i in range(1, 5):
        m = re.search(rf"## Semana {i} — (.+?)\n(.*?)(?=## Semana |\Z)", md, re.S)
        if not m:
            continue
        html += (
            f'<div class="week">'
            f'<p class="week-label">Semana {i}</p>'
            f'<h3 class="week-title">{html_escape(m.group(1).strip())}</h3>'
            f'{md_table_to_html(m.group(2))}</div>'
        )
    return html


def render_guia(md: str) -> str:
    html = ""
    for chunk in re.split(r"\n(?=## )", md):
        chunk = chunk.strip()
        if not chunk.startswith("## ") or chunk.startswith("# Anexo"):
            continue
        lines = chunk.split("\n", 1)
        title = lines[0].replace("## ", "")
        body = lines[1] if len(lines) > 1 else ""
        if body.strip().startswith("|"):
            content = md_table_to_html(body)
        elif "- [" in body:
            items = re.findall(r"- \[ \] (.+)", body)
            content = '<ul class="checks">' + "".join(f"<li>{html_escape(x)}</li>" for x in items) + "</ul>"
        else:
            parts = []
            for p in body.split("\n\n"):
                p = p.strip()
                if not p or p.startswith("|") or p.startswith("- "):
                    continue
                p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html_escape(p))
                parts.append(f"<p>{p}</p>")
            content = "".join(parts)
        html += f'<div class="guia-block"><h3>{html_escape(title)}</h3>{content}</div>'
    return html


CSS = """
@page { size: A4; margin: 0; }
@page :first { margin: 0; }

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 10pt;
  line-height: 1.65;
  color: #1a1a1a;
  background: #fdfcfa;
  -webkit-font-smoothing: antialiased;
}

/* —— CAPA —— */
.cover {
  page-break-after: always;
  padding: 18mm 22mm 20mm;
  background: #fdfcfa;
  display: block;
  position: relative;
  overflow: hidden;
}
.cover::before {
  content: "";
  position: absolute;
  top: -80mm;
  right: -60mm;
  width: 200mm;
  height: 200mm;
  background: radial-gradient(circle, rgba(212,98,42,0.07) 0%, transparent 70%);
  pointer-events: none;
}
.cover-top { position: relative; z-index: 1; }
.cover-line {
  width: 40px;
  height: 3px;
  background: #d4622a;
  border-radius: 2px;
  margin-bottom: 10mm;
}
.cover-eyebrow {
  font-size: 8.5pt;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #d4622a;
  margin-bottom: 6mm;
}
.cover h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 42pt;
  font-weight: 300;
  line-height: 1.05;
  color: #1a1a1a;
  letter-spacing: -0.02em;
  margin-bottom: 8mm;
}
.cover-tagline {
  font-size: 12pt;
  color: #6b6560;
  max-width: 105mm;
  line-height: 1.55;
  font-weight: 400;
}
.cover-stats {
  display: flex;
  gap: 10mm;
  margin-top: 10mm;
  padding-top: 6mm;
  border-top: 1px solid #e8e4df;
}
.cover-stat strong {
  display: block;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 22pt;
  font-weight: 500;
  color: #1a1a1a;
  line-height: 1;
}
.cover-stat span {
  font-size: 8pt;
  color: #9c9690;
  margin-top: 2mm;
  display: block;
}
.cover-bottom {
  position: relative;
  z-index: 1;
  font-size: 8pt;
  color: #b5b0a8;
  border-top: 1px solid #e8e4df;
  padding-top: 4mm;
  margin-top: 12mm;
  display: flex;
  justify-content: space-between;
}

/* —— PÁGINAS INTERNAS —— */
.page {
  padding: 14mm 22mm 16mm;
  background: #fdfcfa;
}
.page-flush { padding-top: 0; }
.page-section { margin-top: 10mm; padding-top: 8mm; border-top: 1px solid #ebe7e2; }

.page-label {
  font-size: 7.5pt;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d4622a;
  margin-bottom: 4mm;
}
.page h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 22pt;
  font-weight: 400;
  color: #1a1a1a;
  letter-spacing: -0.02em;
  margin-bottom: 4mm;
  line-height: 1.2;
}
.page-lead {
  font-size: 10.5pt;
  color: #6b6560;
  max-width: 130mm;
  margin-bottom: 6mm;
  line-height: 1.6;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 4mm;
  margin: 5mm 0;
}
.step {
  display: flex;
  gap: 5mm;
  align-items: flex-start;
}
.step-n {
  flex-shrink: 0;
  width: 8mm;
  height: 8mm;
  border-radius: 50%;
  background: #1a1a1a;
  color: #fff;
  font-size: 8pt;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step p { font-size: 10pt; color: #3d3a36; padding-top: 1mm; }
.step strong { color: #1a1a1a; }

.tip-box {
  background: #fff;
  border: 1px solid #e8e4df;
  border-radius: 10px;
  padding: 4mm 5mm;
  font-size: 9.5pt;
  color: #6b6560;
  margin-top: 5mm;
}
.tip-box strong { color: #1a1a1a; }

/* Sumário */
.toc { list-style: none; }
.toc li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 2.5mm 0;
  border-bottom: 1px solid #ebe7e2;
  font-size: 10pt;
}
.toc li.head {
  font-size: 7.5pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #9c9690;
  border-bottom: none;
  padding-top: 4mm;
  padding-bottom: 1.5mm;
}
.toc li.head:first-child { padding-top: 0; }
.toc .count { color: #d4622a; font-weight: 600; font-size: 9pt; }

/* Abertura de módulo */
.mod-page {
  page-break-before: always;
  padding: 18mm 22mm;
  min-height: 55mm;
  background: #1a1a1a;
  color: #fff;
  position: relative;
  overflow: hidden;
  margin: 0;
}
.mod-page::after {
  content: attr(data-num);
  position: absolute;
  right: 10mm;
  bottom: -15mm;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 120pt;
  font-weight: 300;
  color: rgba(255,255,255,0.04);
  line-height: 1;
  pointer-events: none;
}
.mod-page .mod-idx {
  font-size: 8pt;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #d4622a;
  margin-bottom: 4mm;
}
.mod-page h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 26pt;
  font-weight: 400;
  letter-spacing: -0.02em;
  margin-bottom: 4mm;
  line-height: 1.15;
}
.mod-page p {
  font-size: 10pt;
  color: rgba(255,255,255,0.65);
  max-width: 120mm;
  line-height: 1.55;
}

/* Prompt */
.prompts-wrap { padding: 8mm 22mm 22mm; background: #fdfcfa; }

.prompt {
  page-break-inside: avoid;
  background: #fff;
  border: 1px solid #e8e4df;
  border-radius: 14px;
  padding: 6mm 7mm;
  margin-bottom: 6mm;
  box-shadow: 0 1px 3px rgba(26,26,26,0.04);
}
.prompt-top {
  display: flex;
  align-items: center;
  gap: 4mm;
  margin-bottom: 3mm;
}
.prompt-num {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 18pt;
  font-weight: 500;
  color: #d4622a;
  line-height: 1;
  min-width: 10mm;
}
.prompt-title {
  font-size: 11pt;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.35;
}
.prompt-when {
  font-size: 8.5pt;
  color: #9c9690;
  margin-bottom: 4mm;
  padding-left: 14mm;
}
.prompt-code {
  background: #f7f5f2;
  border-radius: 8px;
  padding: 4mm 5mm;
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 7.8pt;
  line-height: 1.55;
  white-space: pre-wrap;
  color: #2d2a26;
  border: 1px solid #ebe7e2;
}
.prompt-hint {
  margin-top: 3mm;
  padding-left: 14mm;
  font-size: 8pt;
  color: #9c9690;
}

/* Anexos */
.annex-wrap { padding: 0 22mm 22mm; background: #fdfcfa; }
.week { margin-bottom: 8mm; page-break-inside: avoid; }
.week-label {
  font-size: 7.5pt;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #d4622a;
  margin-bottom: 2mm;
}
.week-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 13pt;
  font-weight: 400;
  margin-bottom: 4mm;
  color: #1a1a1a;
}
.table-wrap { overflow: hidden; border-radius: 10px; border: 1px solid #e8e4df; }
table { width: 100%; border-collapse: collapse; font-size: 8pt; }
th {
  background: #f7f5f2;
  text-align: left;
  padding: 2.5mm 3.5mm;
  font-weight: 600;
  font-size: 7.5pt;
  color: #6b6560;
  border-bottom: 1px solid #e8e4df;
}
td {
  padding: 2.5mm 3.5mm;
  border-bottom: 1px solid #f0ece7;
  color: #3d3a36;
  vertical-align: top;
}
tr:last-child td { border-bottom: none; }

.guia-block { margin-bottom: 8mm; page-break-inside: avoid; }
.guia-block h3 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 12pt;
  font-weight: 400;
  margin-bottom: 3mm;
  color: #1a1a1a;
}
.guia-block p { font-size: 9.5pt; color: #6b6560; margin-bottom: 2mm; line-height: 1.6; }
.checks { list-style: none; }
.checks li {
  font-size: 9.5pt;
  color: #6b6560;
  padding: 2mm 0 2mm 6mm;
  position: relative;
  border-bottom: 1px solid #f0ece7;
}
.checks li::before {
  content: "";
  position: absolute;
  left: 0; top: 3.5mm;
  width: 3mm; height: 3mm;
  border-radius: 1px;
  border: 1.5px solid #d4622a;
}

/* Fechamento */
.end {
  page-break-before: always;
  padding: 18mm 22mm;
  background: #fdfcfa;
}
.end h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 28pt;
  font-weight: 300;
  margin-bottom: 4mm;
  letter-spacing: -0.02em;
}
.end-lead { font-size: 11pt; color: #6b6560; max-width: 120mm; margin-bottom: 8mm; }
.end-items { list-style: none; }
.end-items li {
  padding: 3mm 0;
  border-bottom: 1px solid #ebe7e2;
  font-size: 10pt;
  color: #3d3a36;
  display: flex;
  gap: 4mm;
}
.end-items li::before {
  content: "→";
  color: #d4622a;
  flex-shrink: 0;
}
.end-footer {
  margin-top: 12mm;
  font-size: 8pt;
  color: #b5b0a8;
}

@media print {
  .mod-page, .prompt, th {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
"""


def build_cover(subtitle: str, stats: list[tuple[str, str]], footer_left: str, footer_right: str) -> str:
    stats_html = "".join(
        f'<div class="cover-stat"><strong>{html_escape(a)}</strong><span>{html_escape(b)}</span></div>'
        for a, b in stats
    )
    return f"""
    <header class="cover">
      <div class="cover-top">
        <div class="cover-line"></div>
        <p class="cover-eyebrow">Guia de comandos</p>
        <h1>Conteúdo<br>Infinito</h1>
        <p class="cover-tagline">{html_escape(subtitle)}</p>
        <div class="cover-stats">{stats_html}</div>
      </div>
      <div class="cover-bottom">
        <span>{html_escape(footer_left)}</span>
        <span>{html_escape(footer_right)}</span>
      </div>
    </header>"""


def build_prompts_html(prompts: list[dict]) -> str:
    html = '<div class="prompts-wrap">'
    last_mod = None
    for p in prompts:
        mod = p["module_num"]
        if mod and mod != last_mod:
            name, desc = MODULE_DATA.get(mod, (p["module_name"], ""))
            html += f"""
            <div class="mod-page" data-num="{mod.zfill(2)}">
              <p class="mod-idx">Parte {mod}</p>
              <h2>{html_escape(name)}</h2>
              <p>{html_escape(desc)}</p>
            </div>"""
            last_mod = mod
        hint = f'<p class="prompt-hint">{html_escape(p["dica"])}</p>' if p["dica"] else ""
        html += f"""
        <article class="prompt">
          <div class="prompt-top">
            <span class="prompt-num">{p['num']}</span>
            <h3 class="prompt-title">{html_escape(p['title'])}</h3>
          </div>
          <p class="prompt-when">{html_escape(p['quando'])}</p>
          <div class="prompt-code">{html_escape(p['body'])}</div>
          {hint}
        </article>"""
    return html + "</div>"


def build_main_html(prompts: list[dict], bonus_cal: str, guia: str) -> str:
    toc = ""
    for mod, (name, _) in MODULE_DATA.items():
        n = sum(1 for p in prompts if p["module_num"] == mod)
        if n:
            toc += f'<li class="head">Parte {mod}</li><li><span>{html_escape(name)}</span><span class="count">{n}</span></li>'
    toc += '<li class="head">Anexos</li>'
    toc += '<li><span>Calendário editorial — 30 dias</span><span class="count">A</span></li>'
    toc += '<li><span>Protocolo de revisão</span><span class="count">B</span></li>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Conteúdo Infinito</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>

{build_cover(
    "Sistema de produção de conteúdo: calendário de 30 dias, checklist de revisão e comandos por situação.",
    [("30", "dias planejados"), ("1", "checklist anti-genérico"), ("6", "etapas do funil")],
    "Edição 2026",
    "Inclui biblioteca de comandos · ChatGPT grátis",
)}

<div class="page">
  <p class="page-label">Introdução</p>
  <h2>Como usar</h2>
  <p class="page-lead">Este material é um sistema de três partes: calendário (o quê postar), checklist (como revisar) e comandos (como executar cada situação).</p>
  <div class="steps">
    <div class="step"><div class="step-n">1</div><p><strong>Calendário</strong> — use o Anexo A para saber o tema de cada dia.</p></div>
    <div class="step"><div class="step-n">2</div><p><strong>Comando</strong> — abra a seção da sua necessidade e preencha os campos do seu negócio.</p></div>
    <div class="step"><div class="step-n">3</div><p><strong>Checklist</strong> — revise com o Anexo B antes de publicar.</p></div>
  </div>
  <div class="tip-box"><strong>Importante:</strong> a IA gera rascunho. O checklist existe para o conteúdo não parecer genérico.</div>

  <div class="page-section">
    <p class="page-label">Índice</p>
    <h2>O que tem aqui</h2>
    <ul class="toc">{toc}</ul>
  </div>
</div>

{build_prompts_html(prompts)}

<div class="mod-page" data-num="A">
  <p class="mod-idx">Anexo A</p>
  <h2>Calendário de 30 dias</h2>
  <p>Temas diários para manter consistência sem reinventar a roda toda semana.</p>
  <p class="page-lead" style="margin-top:12px;font-size:13px">Nota: a numeração dos dias é independente da numeração dos comandos da biblioteca.</p>
</div>
<div class="annex-wrap">{render_calendar(bonus_cal)}</div>

<div class="mod-page" data-num="B">
  <p class="mod-idx">Anexo B</p>
  <h2>Revisar antes de publicar</h2>
  <p>Checklist para o texto ficar com a cara da sua marca, não genérico.</p>
</div>
<div class="annex-wrap">{render_guia(guia)}</div>

<div class="end">
  <h2>Por onde começar</h2>
  <p class="end-lead">Se estiver em dúvida, teste os comandos 7 (hook), 19 (legenda vendedora) e 41 (calendário semanal) — cobrem gancho, legenda e planejamento da semana.</p>
  <ul class="end-items">
    <li>Execute três comandos com dados reais do seu negócio</li>
    <li>Use o Anexo A para montar o mês</li>
    <li>Publique uma peça revisada pelo Anexo B</li>
  </ul>
  <p class="end-footer">Conteúdo Infinito · Guia de comandos para redes sociais</p>
</div>

</body>
</html>"""


def build_bump_html(items: list[dict]) -> str:
    entries = '<div class="prompts-wrap">'
    for p in items:
        when = f'<p class="prompt-when">{html_escape(p["quando"])}</p>' if p["quando"] else ""
        entries += f"""
        <article class="prompt">
          <div class="prompt-top">
            <span class="prompt-num">{p['num']}</span>
            <h3 class="prompt-title">{html_escape(p['title'])}</h3>
          </div>
          {when}
          <div class="prompt-code">{html_escape(p['body'])}</div>
        </article>"""
    entries += "</div>"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Datas Comemorativas — Conteúdo Infinito</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
{build_cover(
    "Comandos para campanhas sazonais — Dia das Mães, Black Friday, Natal e mais.",
    [("15", "comandos"), ("12+", "datas")],
    "Material extra",
    "Complemento ao guia principal",
)}
<div class="page page-flush">
  <p class="page-label">Extra</p>
  <h2>Campanhas por data</h2>
  <p class="page-lead">Use conforme o calendário comercial. Cada comando gera roteiro, legenda e mensagens.</p>
</div>
{entries}
</body>
</html>"""


def try_pdf_edge(html_path: Path, pdf_path: Path) -> bool:
    for edge in [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]:
        if not edge.exists():
            continue
        try:
            subprocess.run(
                [str(edge), "--headless=new", "--disable-gpu",
                 f"--print-to-pdf={pdf_path.resolve()}", "--no-pdf-header-footer",
                 html_path.resolve().as_uri()],
                check=True, capture_output=True, timeout=180000,
            )
            return pdf_path.exists() and pdf_path.stat().st_size > 1000
        except Exception as e:
            print(f"Edge: {e}")
    return False


def main():
    ENTREGA.mkdir(exist_ok=True)
    prompts = parse_prompts(read_text(PRODUTO / "prompts-raw.md"))
    bump = parse_order_bump(read_text(PRODUTO / "order-bump-PDF.md"))

    main_html = ENTREGA / "Conteudo-Infinito-IA.html"
    bump_html = ENTREGA / "Order-Bump-Datas.html"
    main_html.write_text(
        build_main_html(prompts, read_text(PRODUTO / "bonus-calendario-30.md"), read_text(PRODUTO / "guia-uso-ia.md")),
        encoding="utf-8",
    )
    bump_html.write_text(build_bump_html(bump), encoding="utf-8")

    main_pdf = ENTREGA / "Conteudo-Infinito-IA.pdf"
    bump_pdf = ENTREGA / "Order-Bump-Datas.pdf"
    ok1 = try_pdf_edge(main_html, main_pdf)
    ok2 = try_pdf_edge(bump_html, bump_pdf)

    zip_path = ENTREGA / "Conteudo-Infinito-IA-PACK.zip"
    leia_me = ENTREGA / "LEIA-ME.txt"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in [main_pdf, bump_pdf, main_html, bump_html]:
            if f.exists():
                zf.write(f, f.name)
        if leia_me.exists():
            zf.write(leia_me, leia_me.name)

    print(f"OK: {len(prompts)} comandos | visual editorial premium")
    if ok1:
        print(f"PDF: {main_pdf} ({main_pdf.stat().st_size // 1024} KB)")
    if ok2:
        print(f"PDF: {bump_pdf} ({bump_pdf.stat().st_size // 1024} KB)")
    print(f"HTML: {main_html}")
    print(f"ZIP: {zip_path}")


if __name__ == "__main__":
    main()
