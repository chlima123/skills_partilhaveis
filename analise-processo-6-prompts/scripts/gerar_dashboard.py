#!/usr/bin/env python3
# ============================================================
# gerar_dashboard.py
# Gera um Dashboard HTML single-file a partir das etapas da
# análise de processo (6 prompts encadeados).
#
# Entrada : --dir <pasta_saida>   (contém etapa_1.md .. etapa_6.md)
#           --titulo "..."         (opcional)
#           --out  <arquivo.html>  (opcional; default RELATORIO_FINAL.html na pasta)
# Saída   : dashboard HTML autocontido (CSS+JS inline, abre no navegador)
#
# Stdlib apenas (sem pip). Markdown → HTML por um parser mínimo próprio.
# Método: MAPEAR -> DECOMPOR -> CRUZAR -> COMPARAR -> TESTAR -> AUDITAR
# ============================================================
import argparse, html as _html, json, os, re, sys
from datetime import datetime

ETAPAS = [
    ("MAPEAR",   "Mapa do processo"),
    ("DECOMPOR", "Decomposição do caso"),
    ("CRUZAR",   "Cruzamento fatos × provas"),
    ("COMPARAR", "Comparação das teses"),
    ("TESTAR",   "Pontos que merecem atenção"),
    ("AUDITAR",  "Relatório executivo + auditoria"),
]

def esc(s: str) -> str:
    return _html.escape(s, quote=False)

def inline(s: str) -> str:
    """Markdown inline -> HTML. Escapa primeiro, então aplica marcações."""
    s = esc(s)
    # código inline
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    # negrito / itálico
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
    # links [texto](url)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    # destaca [VERIFICAR]
    s = re.sub(r'\[VERIFICAR\]', r'<span class="vrf">[VERIFICAR]</span>', s, flags=re.I)
    return s

def md_to_html(md: str) -> str:
    """Parser markdown mínimo: títulos, listas, tabelas, citação, régua, parágrafos."""
    out, i = [], 0
    lines = md.replace('\r\n', '\n').split('\n')
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip():
            i += 1; continue
        # régua
        if re.match(r'^\s*(-{3,}|\*{3,})\s*$', line):
            out.append('<hr>'); i += 1; continue
        # título
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lvl = min(len(m.group(1)) + 2, 6)  # h1→h3 dentro do card
            out.append(f'<h{lvl}>{inline(m.group(2).strip())}</h{lvl}>'); i += 1; continue
        # tabela (linha com | e próxima = separador)
        if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:\-|]+\|[\s:\-|]*$', lines[i+1]):
            header = [c.strip() for c in line.strip().strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            th = ''.join(f'<th>{inline(c)}</th>' for c in header)
            tr = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows)
            out.append(f'<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>')
            continue
        # citação
        if re.match(r'^\s*>', line):
            buf = []
            while i < len(lines) and re.match(r'^\s*>', lines[i]):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
            out.append('<blockquote>' + '<br>'.join(inline(b) for b in buf) + '</blockquote>')
            continue
        # lista (ul/ol)
        m = re.match(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$', line)
        if m:
            ordered = m.group(2)[0].isdigit()
            tag = 'ol' if ordered else 'ul'
            items = []
            while i < len(lines):
                mm = re.match(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$', lines[i])
                if not mm: break
                items.append(f'<li>{inline(mm.group(3).strip())}</li>'); i += 1
            out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
            continue
        # parágrafo (agrupa linhas seguidas)
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|>|\s*([-*+]|\d+[.)])\s)', lines[i]) and '|' not in lines[i]:
            buf.append(lines[i].strip()); i += 1
        out.append('<p>' + inline(' '.join(buf)) + '</p>')
    return '\n'.join(out)

def count_verificar(texto: str) -> int:
    return len(re.findall(r'\[VERIFICAR\]', texto, flags=re.I))

def main():
    ap = argparse.ArgumentParser(description="Dashboard HTML da análise de processo (6 prompts).")
    ap.add_argument('--dir', required=True, help="pasta com etapa_1.md .. etapa_6.md")
    ap.add_argument('--titulo', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--template', default=None, help="caminho do template (default: assets/ ao lado do script)")
    a = ap.parse_args()

    outdir = os.path.abspath(a.dir)
    if not os.path.isdir(outdir):
        sys.exit(f"[erro] pasta não encontrada: {outdir}")

    here = os.path.dirname(os.path.abspath(__file__))
    tpl_path = a.template or os.path.join(here, '..', 'assets', 'dashboard_template.html')
    tpl_path = os.path.abspath(tpl_path)
    if not os.path.isfile(tpl_path):
        sys.exit(f"[erro] template não encontrado: {tpl_path}")
    tpl = open(tpl_path, encoding='utf-8').read()

    titulo = a.titulo or os.path.basename(outdir.rstrip('/'))
    titulo = re.sub(r'^analise_?', '', titulo)
    titulo = titulo.replace('_', ' ').strip() or 'Análise de processo'

    sections, total_ctx = [], 0
    for n, (nome, label) in enumerate(ETAPAS, 1):
        fp = os.path.join(outdir, f'etapa_{n}.md')
        if os.path.isfile(fp):
            raw = open(fp, encoding='utf-8').read().strip()
        else:
            raw = f'> Etapa {n} não encontrada (`etapa_{n}.md` ausente na pasta).'
            print(f"[aviso] etapa_{n}.md ausente — placeholder incluído.", file=sys.stderr)
        # remove um eventual título H1/H2 duplicado do próprio arquivo ("Etapa N — ...")
        raw = re.sub(r'^#{1,3}\s*Etapa\s*\d+\s*[—\-–:].*\n', '', raw, count=1)
        total_ctx += count_verificar(raw)
        sections.append({"n": n, "kicker": nome, "label": label, "html": md_to_html(raw)})

    data_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    meta = f"{len(sections)} etapas · MAPEAR → DECOMPOR → CRUZAR → COMPARAR → TESTAR → AUDITAR"
    aviso = ("Velocidade não significa leitura infalível. Confira se todos os arquivos/páginas foram "
             "efetivamente processados e valide no documento original toda informação decisiva. "
             "A decisão jurídica exige conferência profissional.")
    credito = ("Método / prompts: <a href=\"https://www.instagram.com/p/DeCOYE1FgZ7/\" target=\"_blank\" "
               "rel=\"noopener\">@advogadotuliosilveira</a>")

    html_out = (tpl
                .replace('__TITULO__', esc(titulo))
                .replace('__META__', esc(meta))
                .replace('__DATA__', esc(data_str))
                .replace('__AVISO__', aviso)
                .replace('__CREDITO__', credito)
                .replace('__SECTIONS_JSON__', json.dumps(sections, ensure_ascii=False)))

    out_path = a.out or os.path.join(outdir, 'RELATORIO_FINAL.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_out)

    print(f">> Dashboard: {out_path}")
    print(f">> Etapas   : {len(sections)}")
    print(f">> [VERIFICAR] no relatório: {total_ctx}")

if __name__ == '__main__':
    main()
