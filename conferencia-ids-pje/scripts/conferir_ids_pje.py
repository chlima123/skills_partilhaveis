#!/usr/bin/env python3
"""conferir_ids_pje.py — conferência determinística dos IDs do PJe.

Uso:
    python3 conferir_ids_pje.py --peca peca.docx --autos consulta.pdf
    python3 conferir_ids_pje.py --peca peca.docx --autos consulta.pdf \
        --valores "405,51" "664,44" "811,02" --out conferencia.md

Faz a parte mecânica da conferência (a interpretação é do agente):
  1. texto da peça (.docx por zipfile, ou .pdf/.txt);
  2. autos página a página (PyMuPDF; cai para `pdftotext -layout`);
  3. bloco `Documentos / Id. / Data da Assinatura / Documento / Tipo` da capa
     -> dict ID -> (data, hora, rótulo, tipo); aceita os DOIS layouts de extração
     (linha por campo, do PyMuPDF, e linha por registro, do pdftotext -layout);
  4. mapa página -> ID pelo rodapé `Num. <ID> - Pág. <N>` (intervalo de páginas de cada
     documento, sem depender da ordem da capa);
  5. IDs citados na peça (`ID 12345678`, `IDs ... e ...`, `id. 123456789`);
  6. por ID citado: existe na capa? rótulo/tipo/data, intervalo de páginas, nº de
     ocorrências literais nos autos, signatário do rodapé;
  7. IDs da capa NÃO citados que estão no MESMO lote (mesma data/hora de assinatura) de um
     ID citado — é onde costuma estar o documento que a peça queria citar;
  8. ocorrências literais dos valores de --valores, com o ID dono de cada página.

Saída: relatório Markdown (stdout ou --out). Exit 0 = rodou; exit 2 = entrada ilegível.
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import subprocess
import sys
import tempfile
import zipfile

RE_RODAPE = re.compile(r"Num\.\s*(\d{7,9})\s*-\s*P[áa]g\.\s*(\d+)")
RE_LINHA_CAPA = re.compile(
    r"^\s*(\d{7,9})\s+(\d{2}/\d{2}/\d{4})\s+(?:(\d{2}:\d{2})\s+)?(.+?)\s*$", re.M
)
RE_CITACAO = re.compile(r"(?:[Ii][Dd]s?\.?\s*:?\s*|id\.\s*)(\d{7,10})", re.M)
RE_ASSINATURA = re.compile(
    r"Assinado eletronicamente por:\s*([^-]+?)\s*-\s*(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})"
)
RE_SO_ID = re.compile(r"^\d{7,9}$")
RE_DATA = re.compile(r"^\d{2}/\d{2}/\d{4}$")
RE_HORA = re.compile(r"^\d{2}:\d{2}$")


# --------------------------------------------------------------------------- extração
def texto_docx(caminho: str) -> str:
    """`.docx` é zip+XML: não exige python-docx."""
    import html

    with zipfile.ZipFile(caminho) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = xml.replace("</w:p>", "\n")
    txt = html.unescape(re.sub(r"<[^>]+>", "", xml))
    linhas = [l.strip() for l in txt.split("\n")]
    # o `wp:posOffset` das imagens sobrevive ao strip como linha numérica órfã
    linhas = [l for l in linhas if l and not re.fullmatch(r"-?\d+(\.\d+)?", l)]
    return re.sub(r"[ \t]{2,}", " ", "\n".join(linhas))


def paginas_pdf(caminho: str) -> list[str]:
    """Páginas do PDF. PyMuPDF se existir; senão `pdftotext -layout`."""
    try:
        import fitz  # PyMuPDF

        with fitz.open(caminho) as doc:
            return [p.get_text() for p in doc]
    except ImportError:
        pass
    tmp = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    tmp.close()
    try:
        subprocess.run(["pdftotext", "-layout", caminho, tmp.name], check=True)
        with open(tmp.name, encoding="utf-8", errors="replace") as fh:
            return [p for p in fh.read().split("\f") if p.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:  # pragma: no cover
        raise SystemExit(
            f"precisa de PyMuPDF (`pip install pymupdf`) ou poppler-utils: {exc}"
        ) from exc
    finally:
        os.unlink(tmp.name)


def texto_arquivo(caminho: str) -> str:
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".docx":
        return texto_docx(caminho)
    if ext == ".pdf":
        return "\n\f\n".join(paginas_pdf(caminho))
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# --------------------------------------------------------------------------- capa
def capa_por_campos(paginas: list[str], limite: int = 12) -> dict[str, dict]:
    """Layout do PyMuPDF: um campo por linha (ID, data, [hora], documento, tipo)."""
    linhas: list[str] = []
    for pag in paginas[:limite]:
        linhas += [l.strip() for l in pag.split("\n") if l.strip()]
    try:
        i = linhas.index("Id.")
    except ValueError:
        return {}
    saida: dict[str, dict] = {}
    j = i + 1
    while j < len(linhas):
        if not RE_SO_ID.match(linhas[j]):
            j += 1
            continue
        ident = linhas[j]
        k = j + 1
        data = hora = ""
        if k < len(linhas) and RE_DATA.match(linhas[k]):
            data = linhas[k]
            k += 1
            if k < len(linhas) and RE_HORA.match(linhas[k]):
                hora = linhas[k]
                k += 1
        if k >= len(linhas):
            break
        rotulo = linhas[k]
        k += 1
        tipo = linhas[k] if k < len(linhas) and not RE_SO_ID.match(linhas[k]) else rotulo
        if data:
            saida[ident] = {"data": data, "hora": hora, "rotulo": rotulo, "tipo": tipo}
        j = k + 1
    return saida


def capa_por_linhas(paginas: list[str], limite: int = 12) -> dict[str, dict]:
    """Layout do `pdftotext -layout`: um registro por linha, colunas separadas por 2+ espaços."""
    saida: dict[str, dict] = {}
    for pag in paginas[:limite]:
        for linha in pag.split("\n"):
            m = RE_LINHA_CAPA.match(linha)
            if not m:
                continue
            ident, data, hora, resto = m.groups()
            partes = [p.strip() for p in re.split(r"\s{2,}", resto.strip()) if p.strip()]
            if not partes:
                continue
            saida[ident] = {
                "data": data,
                "hora": hora or "",
                "rotulo": partes[0],
                "tipo": partes[-1] if len(partes) > 1 else partes[0],
            }
    return saida


def parse_capa(paginas: list[str], limite: int = 12) -> dict[str, dict]:
    """Tenta os dois layouts e devolve o que reconhecer mais documentos."""
    a = capa_por_campos(paginas, limite)
    b = capa_por_linhas(paginas, limite)
    return a if len(a) >= len(b) else b


def mapa_paginas(paginas: list[str]) -> dict[int, dict]:
    """página (1-based) -> {id, pagina_doc} pelo rodapé `Num. <ID> - Pág. <N>`."""
    mapa: dict[int, dict] = {}
    for i, pag in enumerate(paginas, 1):
        achados = RE_RODAPE.findall(pag)
        if achados:
            ident, pag_doc = collections.Counter(achados).most_common(1)[0][0]
            mapa[i] = {"id": ident, "pagina_doc": pag_doc}
    return mapa


def intervalos(mapa: dict[int, dict]) -> dict[str, dict]:
    por_id: dict[str, list[int]] = collections.defaultdict(list)
    for pag, info in mapa.items():
        por_id[info["id"]].append(pag)
    return {
        i: {"ini": min(p), "fim": max(p), "n": len(p)} for i, p in por_id.items()
    }


def signatarios(paginas: list[str], mapa: dict[int, dict]) -> dict[str, set]:
    out: dict[str, set] = collections.defaultdict(set)
    for pag, info in mapa.items():
        for m in RE_ASSINATURA.finditer(paginas[pag - 1]):
            out[info["id"]].add(f"{m.group(1).strip()} ({m.group(2)})")
    return out


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Confere os IDs do PJe citados numa peça contra os autos.")
    ap.add_argument("--peca", required=True, help="peça (.docx, .pdf ou .txt)")
    ap.add_argument("--autos", required=True, help="consulta do processo (.pdf do PJe ou .txt)")
    ap.add_argument("--valores", nargs="*", default=[], help="valores a contar literalmente")
    ap.add_argument("--out", help="grava o relatório Markdown aqui (default: stdout)")
    args = ap.parse_args()

    for caminho in (args.peca, args.autos):
        if not os.path.exists(caminho):
            print(f"não existe: {caminho}", file=sys.stderr)
            return 2

    peca = texto_arquivo(args.peca)
    if args.autos.lower().endswith(".pdf"):
        paginas = paginas_pdf(args.autos)
    else:
        paginas = [p for p in texto_arquivo(args.autos).split("\f") if p.strip()]
    autos = "\n\f\n".join(paginas)

    capa = parse_capa(paginas)
    mapa = mapa_paginas(paginas)
    faixas = intervalos(mapa)
    assin = signatarios(paginas, mapa)

    citados: list[str] = []
    for m in RE_CITACAO.finditer(peca):
        if m.group(1) not in citados:
            citados.append(m.group(1))
    # segunda passada: IDs soltos (sem o prefixo "ID"), aceitos só se existirem nos autos —
    # a peça escreve "faturas de IDs 67106666 e 67106668" e o segundo vem sem prefixo
    for tok in re.findall(r"\b\d{8,9}\b", peca):
        if tok in citados:
            continue
        if tok in capa or tok in faixas or tok in autos:
            citados.append(tok)

    L: list[str] = []
    add = L.append
    add("# Conferência dos IDs do PJe")
    add("")
    add(f"- Peça: `{os.path.basename(args.peca)}` ({len(peca)} chars)")
    add(f"- Autos: `{os.path.basename(args.autos)}` ({len(paginas)} páginas, {len(autos)} chars)")
    add(f"- Documentos listados na capa: **{len(capa)}** · páginas com rodapé de ID: **{len(mapa)}**")
    add(f"- IDs citados na peça: **{len(citados)}** → {', '.join(citados) if citados else '—'}")
    add("")

    add("## ID por ID")
    add("")
    add("| ID citado | Na capa? | Rótulo da capa | Tipo | Data | Págs. no extrato | Ocorr. nos autos |")
    add("|---|---|---|---|---|---|---|")
    for ident in citados:
        d = capa.get(ident)
        faixa = faixas.get(ident)
        ocorr = len(re.findall(re.escape(ident), autos))
        add(
            "| `{}` | {} | {} | {} | {}{} | {} | {} |".format(
                ident,
                "sim" if d else "**não consta**",
                (d or {}).get("rotulo", "—"),
                (d or {}).get("tipo", "—"),
                (d or {}).get("data", "—"),
                (" " + d["hora"]) if d and d.get("hora") else "",
                f"{faixa['ini']}–{faixa['fim']} ({faixa['n']}p)" if faixa else "—",
                ocorr,
            )
        )
    add("")

    na_capa = [i for i in citados if i in capa]
    fora = [i for i in citados if i not in capa]
    if fora:
        add("## IDs citados que NÃO estão na capa desta consulta")
        add("")
        add("Provável numeração de 1º grau (ou de outra instância da consulta). **Não converta entre as")
        add("famílias pela ordem da lista** — compare conteúdo (total citado, competência, partes):")
        for ident in fora:
            ocorr = len(re.findall(re.escape(ident), autos))
            faixa = faixas.get(ident)
            add(
                f"- `{ident}` — {ocorr} ocorrência(s) no texto dos autos"
                + (f", páginas {faixa['ini']}–{faixa['fim']}" if faixa else "")
            )
        add("")

    if assin:
        add("## Signatário por ID (rodapé `/Assinado eletronicamente por/`)")
        add("")
        for ident in citados:
            if ident in assin:
                add(f"- `{ident}`: " + "; ".join(sorted(assin[ident])))
        add("")

    lotes: dict[tuple, list[str]] = collections.defaultdict(list)
    for ident, d in capa.items():
        lotes[(d["data"], d["hora"])].append(ident)
    correlatos = []
    vistos: set[tuple] = set()
    for ident in na_capa:
        d = capa[ident]
        chave = (d["data"], d["hora"])
        if chave in vistos:
            continue    # o mesmo lote já foi listado por outro ID citado
        irmaos = sorted(x for x in lotes[chave] if x not in citados)
        if irmaos:
            vistos.add(chave)
            correlatos.append((ident, d, irmaos))
    if correlatos:
        add("## Documentos do MESMO lote de um ID citado — não citados pela peça")
        add("")
        add("É aqui que costuma estar o documento que a peça queria citar (o relatório certo, o")
        add("comprovante de pagamento, o demonstrativo):")
        for ident, d, irmaos in correlatos:
            add(f"- lote de `{ident}` ({d['data']} {d['hora']} — {d['rotulo']}):")
            for x in irmaos:
                dd = capa[x]
                add(f"    - `{x}` — {dd['rotulo']} ({dd['tipo']})")
        add("")

    if args.valores:
        add("## Ocorrências literais dos valores afirmados")
        add("")
        add("| Valor | Na peça | Nos autos | IDs que os contêm |")
        add("|---|---|---|---|")
        offsets, acc = [], 0
        for i, pag in enumerate(paginas, 1):
            offsets.append((acc, acc + len(pag), i))
            acc += len(pag) + len("\n\f\n")
        for valor in args.valores:
            achados = list(re.finditer(re.escape(valor), autos))
            donos: list[str] = []
            for m in achados:
                for ini, fim, pag in offsets:
                    if ini <= m.start() < fim:
                        donos.append(mapa.get(pag, {}).get("id", "?"))
                        break
            add(
                f"| {valor} | {len(re.findall(re.escape(valor), peca))} | {len(achados)} | "
                + (", ".join(f"`{x}`" for x in dict.fromkeys(donos)) if donos else "—")
                + " |"
            )
        add("")

    relatorio = "\n".join(L)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(relatorio)
        print(f"relatório: {args.out} ({len(relatorio)} chars)")
    else:
        print(relatorio)
    return 0


if __name__ == "__main__":
    sys.exit(main())
