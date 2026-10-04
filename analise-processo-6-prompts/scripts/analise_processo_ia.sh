#!/usr/bin/env bash
# ============================================================
# analise_processo_ia.sh
# Pipeline de análise de processo jurídico com IA em 6 etapas
#   MAPEAR -> DECOMPOR -> CRUZAR -> COMPARAR -> TESTAR -> AUDITAR
#
# Fonte dos prompts: @advogadotuliosilveira
#   https://www.instagram.com/p/DeCOYE1FgZ7/
#
# Uso:
#   ./analise_processo_ia.sh <processo.(pdf|txt|md)> [pasta_saida]
#   ./analise_processo_ia.sh --prompts      # so imprime os 6 prompts
#
# Requer um CLI de IA no PATH: claude (Claude Code) ou codex (Codex CLI).
# Escolha com a env ANALISE_CLI=claude|codex|echo  (default: claude)
# ============================================================
set -euo pipefail

# ---------- Prompts (verbatim, ver comentario de fonte acima) ----------
read -r -d '' PROMPT_1 <<'EOF' || true
Analise o processo e identifique partes, objeto da demanda, fase processual, principais peças, pedidos, decisões e provas. Organize também os acontecimentos relevantes em ordem cronológica. Ainda não apresente conclusões.
EOF

read -r -d '' PROMPT_2 <<'EOF' || true
Separe as informações em: fatos incontroversos, fatos controvertidos, alegações do autor, alegações do réu, teses jurídicas, pedidos, provas, decisões e questões ainda pendentes.
EOF

read -r -d '' PROMPT_3 <<'EOF' || true
Para cada fato controvertido, identifique quais provas existem nos autos. Classifique o suporte como consistente, parcial, contraditório ou ausente e indique onde cada elemento foi localizado.
EOF

read -r -d '' PROMPT_4 <<'EOF' || true
Para cada questão relevante, coloque lado a lado: tese do autor → tese do réu → prova do autor → prova do réu → argumento favorável → argumento contrário.
EOF

read -r -d '' PROMPT_5 <<'EOF' || true
Identifique contradições, fatos sem prova, documentos relevantes aparentemente não explorados, argumentos não enfrentados, lacunas probatórias e questões capazes de influenciar a estratégia processual.
EOF

read -r -d '' PROMPT_6 <<'EOF' || true
Crie um relatório executivo contendo linha do tempo, pedidos, controvérsias, teses, provas, contradições, fragilidades e pontos que exigem providência. Depois, audite suas conclusões e marque como [VERIFICAR] tudo que não estiver suficientemente sustentado pelos autos.
EOF

PROMPTS=("$PROMPT_1" "$PROMPT_2" "$PROMPT_3" "$PROMPT_4" "$PROMPT_5" "$PROMPT_6")
ETAPAS=("MAPEAR - Mapa do processo" \
        "DECOMPOR - Decomposição do caso" \
        "CRUZAR - Cruzamento fatos x provas" \
        "COMPARAR - Comparação das teses" \
        "TESTAR - Pontos que merecem atenção" \
        "AUDITAR - Relatório executivo + auditoria")

print_prompts() {
  echo "Método: MAPEAR -> DECOMPOR -> CRUZAR -> COMPARAR -> TESTAR -> AUDITAR"
  echo "Fonte: @advogadotuliosilveira - https://www.instagram.com/p/DeCOYE1FgZ7/"
  echo
  local i
  for i in $(seq 0 5); do
    echo "PROMPT $((i+1)): ${ETAPAS[$i]}"
    echo "${PROMPTS[$i]}"
    echo "---"
  done
  echo "Velocidade não significa leitura infalível: confira se todos os"
  echo "arquivos/páginas foram processados e valide no original toda"
  echo "informação decisiva. A decisão jurídica exige conferência profissional."
}

if [[ "${1:-}" == "--prompts" || "${1:-}" == "-p" ]]; then
  print_prompts
  exit 0
fi

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <processo.(pdf|txt|md)> [pasta_saida]" >&2
  echo "     $0 --prompts" >&2
  exit 2
fi

PROCESSO="$1"
[[ -f "$PROCESSO" ]] || { echo "Arquivo não encontrado: $PROCESSO" >&2; exit 1; }

PROC_DIR="$(cd "$(dirname "$PROCESSO")" && pwd)"
PROC_NAME="$(basename "$PROCESSO")"
BASE="${PROC_NAME%.*}"

OUTDIR="${2:-$PROC_DIR/analise_${BASE}_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$OUTDIR"

# Se for PDF e houver pdftotext, gera versão texto (ajuda o modelo em arquivos grandes).
TEXTO_REF="$PROC_NAME"
if [[ "$PROC_NAME" == *.pdf ]] && command -v pdftotext >/dev/null 2>&1; then
  pdftotext -layout "$PROCESSO" "$OUTDIR/processo.txt" 2>/dev/null || true
  [[ -s "$OUTDIR/processo.txt" ]] && TEXTO_REF="processo.txt"
fi

CLI="${ANALISE_CLI:-claude}"
case "$CLI" in
  claude) CLI_CMD=(claude -p) ;;
  codex)  CLI_CMD=(codex exec) ;;
  echo)   CLI_CMD=(echo) ;;
  *) echo "ANALISE_CLI inválido: $CLI (use claude|codex|echo)" >&2; exit 2 ;;
esac

echo ">> Processo : $PROC_DIR/$TEXTO_REF"
echo ">> Saída    : $OUTDIR"
echo ">> CLI      : $CLI"
echo

CTX="$OUTDIR/_contexto_acumulado.md"
: > "$CTX"

for i in $(seq 0 5); do
  N=$((i+1))
  LABEL="${ETAPAS[$i]}"
  OUT="$OUTDIR/etapa_${N}.md"
  echo "== Etapa ${N}/6 — ${LABEL}"

  PREAMBULO="Você é um assistente jurídico. O processo a analisar é o arquivo '${TEXTO_REF}' no diretório atual. Trabalhe em etapas e responda em português do Brasil, de forma estruturada. Não invente dados: se algo não estiver nos autos, marque [VERIFICAR]."

  if [[ $i -gt 0 ]]; then
    PREAMBULO="${PREAMBULO}
Segue o resultado das etapas anteriores para você continuar a partir dele:

$(cat "$CTX")
---"
  fi

  PROMPT_FULL="${PREAMBULO}

ETAPA ${N} — ${LABEL}
${PROMPTS[$i]}"

  ( cd "$PROC_DIR" && "${CLI_CMD[@]}" "$PROMPT_FULL" ) | tee "$OUT"

  {
    echo "## Etapa ${N} — ${LABEL}"
    echo
    cat "$OUT"
    echo
  } >> "$CTX"
done

REL="$OUTDIR/RELATORIO_FINAL.md"
{
  echo "# Relatório de análise — ${BASE}"
  echo
  echo "*Gerado em $(date '+%d/%m/%Y %H:%M') — método MAPEAR → DECOMPOR → CRUZAR → COMPARAR → TESTAR → AUDITAR*"
  echo "*Fonte dos prompts: @advogadotuliosilveira*"
  echo
  echo "> Atenção: velocidade não significa leitura infalível. Confira se todos os"
  echo "> arquivos/páginas foram processados e valide no documento original toda"
  echo "> informação decisiva ([VERIFICAR]). A decisão jurídica exige conferência profissional."
  echo
  cat "$CTX"
} > "$REL"

echo
echo ">> Relatório final: $REL"
