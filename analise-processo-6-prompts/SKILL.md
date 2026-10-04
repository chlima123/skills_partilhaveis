---
name: analise-processo-6-prompts
description: "Use ao analisar processo com os 6 prompts encadeados."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [direito, processo, prompts, ia, analise, triagem, verificar, claude, codex, dashboard, html]
    related_skills: [analise-sentenca-3-prompts, parecer-recursal-civel-mppe, codigo-processo-civil, pdf-ocr-portuguese, ia-pesquisa-jurisprudencial, dashboard-navegavel-documento]
---

# Análise de Processo — 6 Prompts Encadeados (método @advogadotuliosilveira)

Analisa um **processo extenso** (ex.: 500 páginas) em **seis etapas encadeadas**, em vez de um
único pedido genérico ("Analise este processo."). Cada etapa recebe o resultado acumulado das
anteriores e produz uma saída própria; a última consolida tudo num relatório auditado —
**entregue como dashboard HTML navegável**.

Método: **MAPEAR → DECOMPOR → CRUZAR → COMPARAR → TESTAR → AUDITAR**.

Fonte dos prompts: perfil Instagram **@advogadotuliosilveira** —
`https://www.instagram.com/p/DeCOYE1FgZ7/` (04/10/2026).

## When to Use (Quando usar)

- Charles pede "analise o processo", "faça a análise em etapas", "os 6 prompts do processo"
- Subiu (ou vai subir) um **processo volumoso** (PDF/DOCX/txt) e quer triagem estruturada
- Preparação do **insumo** de uma peça (parecer, recurso, memorial) antes de escrever
- Quer o mapa do processo, o cruzamento fato × prova e o relatório executivo **em dashboard** num fluxo só

**Não usar para** analisar **uma sentença** com diagnóstico recursal — isso é
`analise-sentenca-3-prompts` (método distinto, 3 prompts, foco em fundamentação/art. 489).
Aqui o objeto é o **processo inteiro**: partes, provas, controvérsias, estratégia.

## A lógica do método

Um processo de centenas de páginas **não** deve ser analisado num só pedido de IA. Separe em
etapas, cada uma com um papel: a saída de cada prompt alimenta o próximo. O encadeamento é o
método — isolar um prompt (rodar só o 3, por exemplo) quebra o resultado.

| Etapa | Nome | Objetivo |
|---|---|---|
| 1 | MAPEAR | Mapa do processo: partes, objeto, fase, peças, pedidos, decisões, provas + linha do tempo (sem conclusões) |
| 2 | DECOMPOR | Fatos controvertidos/incontroversos, alegações de cada parte, teses, pedidos, provas, pendências |
| 3 | CRUZAR | Para cada fato controvertido, qual prova existe e qual o suporte (consistente/parcial/contraditório/ausente) |
| 4 | COMPARAR | Tese do autor × tese do réu × prova de cada um × argumento favorável × contrário |
| 5 | TESTAR | Contradições, fatos sem prova, documentos não explorados, argumentos não enfrentados, lacunas |
| 6 | AUDITAR | Relatório executivo + auditoria, marcando `[VERIFICAR]` o que não estiver sustentado nos autos |

## Os 6 prompts (verbatim — usar sem reescrever)

### PROMPT 1 — MAPEAR (Mapa do processo)
> Analise o processo e identifique partes, objeto da demanda, fase processual, principais peças, pedidos, decisões e provas. Organize também os acontecimentos relevantes em ordem cronológica. Ainda não apresente conclusões.

### PROMPT 2 — DECOMPOR (Decomposição do caso)
> Separe as informações em: fatos incontroversos, fatos controvertidos, alegações do autor, alegações do réu, teses jurídicas, pedidos, provas, decisões e questões ainda pendentes.

### PROMPT 3 — CRUZAR (Cruzamento fatos × provas)
> Para cada fato controvertido, identifique quais provas existem nos autos. Classifique o suporte como consistente, parcial, contraditório ou ausente e indique onde cada elemento foi localizado.

### PROMPT 4 — COMPARAR (Comparação das teses)
> Para cada questão relevante, coloque lado a lado: tese do autor → tese do réu → prova do autor → prova do réu → argumento favorável → argumento contrário.

### PROMPT 5 — TESTAR (Pontos que merecem atenção)
> Identifique contradições, fatos sem prova, documentos relevantes aparentemente não explorados, argumentos não enfrentados, lacunas probatórias e questões capazes de influenciar a estratégia processual.

### PROMPT 6 — AUDITAR (Relatório executivo + auditoria)
> Crie um relatório executivo contendo linha do tempo, pedidos, controvérsias, teses, provas, contradições, fragilidades e pontos que exigem providência. Depois, audite suas conclusões e marque como [VERIFICAR] tudo que não estiver suficientemente sustentado pelos autos.

## Caveats do autor (não omitir na entrega)

O post fecha com duas advertências que **fazem parte do método** e devem constar do relatório
(e do banner do topo do dashboard):

- **Velocidade não significa leitura infalível.** Em processos extensos, confira se **todos os
  arquivos e páginas foram efetivamente processados** e valide no **documento original** qualquer
  informação decisiva.
- **A decisão jurídica continua exigindo conferência profissional.** A IA reduz o tempo de
  triagem; não substitui a conferência dos autos.

## Como rodar

### Opção A — script encadeado (empacotado nesta skill)

`scripts/analise_processo_ia.sh` roda as 6 etapas em sequência sobre o arquivo, cada etapa
recebendo o contexto acumulado, e gera `etapa_1.md` … `etapa_6.md` + `RELATORIO_FINAL.md` +
**`RELATORIO_FINAL.html`** (dashboard, gerado automaticamente ao final).

```bash
bash scripts/analise_processo_ia.sh processo.pdf            # pasta de saída padrão
bash scripts/analise_processo_ia.sh processo.pdf /saida/x   # pasta explícita
bash scripts/analise_processo_ia.sh --prompts               # só imprime os 6 prompts
```

- Escolha o CLI de IA com `ANALISE_CLI=claude|codex|echo` (default `claude`).
- Se for PDF e houver `pdftotext`, gera `processo.txt` na pasta para o modelo lidar melhor.
- Uma cópia de trabalho vive em `~/.hermes/scripts/analise_processo_ia.sh`.

### Opção B — encadear no próprio agente (sem CLI externo)

Se for o próprio Hermes a analisar (processo anexado ao chat ou lido do vault), rodar as 6
etapas **em sequência**, colando a saída de cada uma na entrada da seguinte (prompts verbatim
acima). A saída de cada etapa é a entrada da próxima — não paralelizar. Salvar cada etapa em
`etapa_N.md` e, ao final, gerar o dashboard (Opção C).

### Opção C — gerar só o dashboard (a partir das etapas já prontas)

```bash
python3 scripts/gerar_dashboard.py --dir <pasta_da_analise> \
        --titulo "Processo nº ..." --out <pasta>/RELATORIO_FINAL.html
```

- Lê `etapa_1.md` … `etapa_6.md` da pasta e emite um **único HTML autocontido**
  (CSS+JS inline, sem build, sem fetch) — abre direto no navegador (`file://` funciona).
- `--titulo` é opcional (default: nome da pasta). Sem `--out`, grava `RELATORIO_FINAL.html` na pasta.
- Só stdlib (`python3`), sem `pip`. Markdown → HTML por parser mínimo próprio
  (títulos, listas, tabelas, citação, `**negrito**`, `código`, links e `[VERIFICAR]` destacado).
- Etapa ausente vira um placeholder no dashboard (aviso no stderr) — não aborta.

## Dashboard HTML (entregável padrão)

Gerado por `scripts/gerar_dashboard.py` a partir de `assets/dashboard_template.html`.
Mesmo vernáculo do perfil (tema escuro azul-ardósia + acento dourado; ver `dashboard-navegavel-documento`).

- **Uma seção por etapa** (`etapa-1` … `etapa-6`), numeradas, com kicker (MAPEAR/DECOMPOR/…) e corpo
  formatado (títulos, listas, tabelas, citação, código).
- **Sidebar de etapas**: clicar rola até a seção e destaca; a seção ativa é sincronizada ao navegar.
- **Busca full-text** no topo: filtra e destaca ocorrências com `<mark>` e conta "N em M etapa(s)";
  etapas sem ocorrência são ocultadas. `Esc` limpa e restaura todas.
- **Atalhos de teclado**: `/` foca a busca; `←`/`→` (ou `↑`/`↓`) percorrem as etapas; botões `‹` `›` idem.
- **Banner de aviso** com os caveats do autor e **rodapé com o crédito** (`@advogadotuliosilveira`).
- **Botão Imprimir** + CSS `@media print` (imprime todas as etapas legíveis, mesmo as ocultadas pela busca).
- **[VERIFICAR]** renderizado como selo vermelho; contagem de pendências sai no stdout do gerador.

## Regras duras

- **Encadeamento, não paralelismo.** A saída da etapa N entra na etapa N+1. Rodar as 6 "em
  paralelo" produz seis saídas desconexas — exatamente o que o método critica.
- **Não inventar dado.** O que não estiver nos autos vai marcado `[VERIFICAR]` (regra do prompt 6).
- **Validar a cobertura.** Antes de afirmar "analisei tudo", confirmar que o modelo processou
  **todas** as páginas/anexos; se a extração foi parcial, dizer isso e reduzir o escopo declarado.
- **Prompts verbatim.** Não reescrever os seis textos: alterá-los quebra a comparação com o método.
- **Conferência profissional** no rodapé do relatório/dashboard, sempre.

## Entregáveis (padrão do perfil)

| Destino | Conteúdo |
|---|---|
| Arquivos locais | `etapa_1.md` … `etapa_6.md` + `RELATORIO_FINAL.md` + **`RELATORIO_FINAL.html`** (dashboard) |
| Chat | resumo executivo + **caminho absoluto do dashboard** (e link Pages, se publicado) |
| Obsidian (se pedido) | nota em `001_TRABALHO/` com frontmatter, `credito: "@advogadotuliosilveira — https://www.instagram.com/p/DeCOYE1FgZ7/"` e link do dashboard |
| Publicação | dashboard HTML → GitHub Pages quando pedido (skill `github-pages-publish`) |

## Verificação (antes de entregar)

- [ ] `RELATORIO_FINAL.html` existe e abre sem erro de JS (Playwright/servidor local, não só abrir).
- [ ] 6 seções renderizadas; sidebar com 6 links; HUD "1 / 6".
- [ ] Busca filtra + destaca (`<mark>`) e limpar restaura todas as etapas.
- [ ] `←`/`→`/`↑`/`↓` trocam de etapa com o foco fora do input; `/` foca a busca; `Esc` limpa.
- [ ] Selos `[VERIFICAR]` visíveis; contagem bate com o stdout do gerador.
- [ ] Imprimir/PDF inclui todas as etapas (inclusive ocultadas pela busca).
- [ ] Caminho absoluto confirmado na resposta.

## Pitfalls

- **Nunca rodar o prompt 1 sobre trecho parcial** (PDF mal extraído, e-mail em pedaços):
  contamina as etapas 2–5 e o relatório herda a lacuna. Normalizar o texto primeiro
  (PDF digitalizado → `pdf-ocr-portuguese`).
- **Processo sob segredo de justiça / dado sensível**: manter local, **não publicar dashboard**
  (não hospedar em Pages, não anexar em chat público). O HTML fica só no disco/vault.
- **Não confundir com `analise-sentenca-3-prompts`**: lá é diagnóstico de **fundamentação** da
  sentença (art. 489, § 1º, encadeamento de 3 prompts); aqui é triagem do **processo inteiro**
  (6 etapas, foco em provas e estratégia). São métodos de autores diferentes.
- **`ANALISE_CLI` inexistente no PATH** faz o script falhar logo no início — conferir `claude`
  ou `codex` disponível, ou `ANALISE_CLI=echo` para testar o pipeline sem IA.
- **Gerar o dashboard exige `python3`** (stdlib). Se faltar, o `RELATORIO_FINAL.md` já está pronto —
  rodar `gerar_dashboard.py` depois, em qualquer máquina com Python 3.
- **`file://` basta** para abrir o dashboard (tudo inline). Não precisa de servidor nem build;
  para publicar, o mesmo arquivo serve direto em Pages/estático.
- **Título legível**: o default do `--titulo` é o nome da pasta de saída — passe `--titulo` com o
  número/nome do processo quando o nome da pasta não for apresentável.
- **Delegação ao `agy`**: tarefa analítica do próprio agente; conferir disponibilidade antes de
  cogitar delegar (ver `antigravity-delegacao-supervisionada`).

## References

- `scripts/analise_processo_ia.sh` — pipeline encadeado das 6 etapas (prompts verbatim); gera
  `RELATORIO_FINAL.md` e chama o gerador do dashboard.
- `scripts/gerar_dashboard.py` — dashboard HTML single-file a partir de `etapa_1.md` … `etapa_6.md`.
- `assets/dashboard_template.html` — template do dashboard (CSS+JS inline, tema escuro dourado).
- `dashboard-navegavel-documento` — padrão irmão de dashboard navegável (documento/lei).
- `github-pages-publish` — publicar o HTML resultante, se pedido.
- `analise-sentenca-3-prompts` — método irmão (3 prompts) para diagnóstico recursal de sentença.
- Crédito do método: **@advogadotuliosilveira** — `https://www.instagram.com/p/DeCOYE1FgZ7/`.
