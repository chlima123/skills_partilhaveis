---
name: pesquisa-jurisprudencial-ia
description: Pesquisa jurisprudencial com IA usando os 6 prompts, com o relatório publicado diretamente no chat.
---

# Pesquisa Jurisprudencial com IA (6 Prompts)

Aplica os 6 prompts estruturados de pesquisa jurisprudencial sobre um tema jurídico e entrega o relatório diretamente na conversa (sem envio por e-mail, Evernote ou Obsidian).

## Quando usar

- Pedido para pesquisar jurisprudência sobre um tema usando IA
- "aplica os prompts", "usa os 6 prompts", "pesquisa jurisprudencial com IA"
- Compartilhamento de um tema jurídico com pedido de relatório estruturado

## Os 6 prompts (núcleo da skill)

Para cada tema, a pesquisa deve responder a estas 6 perguntas estruturadas:

1. **PESQUISA** — Pesquisar a jurisprudência mais recente sobre o tema, delimitando o escopo exclusivamente às decisões relacionadas.
2. **IDENTIFIQUE O ENTENDIMENTO ATUAL** — Informar o entendimento predominante dos tribunais: posição consolidada, divergência jurisprudencial ou mudança recente.
3. **PRINCIPAIS PRECEDENTES** — Apresentar os principais precedentes, indicando tribunal, número do processo, órgão julgador, data do julgamento e tese firmada.
4. **TESES VINCULANTES** — Verificar súmulas, súmulas vinculantes, recursos repetitivos, temas de repercussão geral, IRDR, IAC ou outros precedentes obrigatórios.
5. **POSIÇÃO CONTRÁRIA** — Assumir a posição da parte contrária e levantar a jurisprudência que possa enfraquecer a tese, explicando os riscos da estratégia.
6. **ORGANIZE A PESQUISA** — Elaborar relatório final: entendimento predominante, decisões favoráveis, decisões desfavoráveis, precedentes obrigatórios, divergências e melhor estratégia argumentativa para a peça.

## Procedimento

### Passo 1 — Coletar o tema
Identificar o tema jurídico a pesquisar. Se não estiver claro, pedir esclarecimento com 2-4 opções concretas (nunca em aberto).

### Passo 2 — Pesquisar jurisprudência (fontes reais)
Para cada um dos 6 prompts, buscar dados reais e verificáveis via `web_search`/`web_search_fast`, priorizando fontes oficiais:
- **STJ** (súmulas, temas repetitivos, jurisprudência em teses)
- **STF** (súmulas vinculantes, repercussão geral)
- Tribunais estaduais/regionais relevantes ao caso
- JusBrasil, Migalhas, ConJur — apenas como apoio doutrinário/noticioso, nunca como fonte de número de processo
- Operadores `site:` para restringir a fontes oficiais quando necessário

**Regra de ouro:** nunca inventar número de processo, tribunal, data ou tese. Se um dado não for encontrado, marcar como "não localizado" em vez de fabricar. Precedentes obrigatórios (súmulas vinculantes, repetitivos, RG, IRDR, IAC) merecem verificação redobrada — são os mais citados em petições e o erro tem custo alto.

### Passo 3 — Compilar o relatório
Estruturar o resultado seguindo os 6 prompts como seções, cada uma com os dados reais encontrados e citação de fonte (tribunal, número, data, link).

### Passo 4 — Publicar no chat
Em vez de enviar por e-mail/Evernote/Obsidian, apresentar o relatório completo diretamente na resposta do chat, formatado em Markdown com as 6 seções acima. Se o relatório for longo, oferecer também a opção de gerar um documento (Word ou artifact) para download, mas o padrão é publicar o conteúdo inline na conversa.

### Passo 5 — Verificar
Revisar se todas as 6 seções foram respondidas, se todo dado citado tem fonte real e se nada foi fabricado antes de enviar a resposta final.

## Pitfalls

- **Nunca fabricar jurisprudência.** Número de processo, tribunal, data e tese devem vir de fonte real. Se não achar, escrever "não localizado" e seguir.
- **Precedentes obrigatórios** (SV, repetitivos, RG, IRDR, IAC) merecem verificação dupla.
- **Tema ambíguo → perguntar com opções concretas**, nunca em aberto.
- **Não usar e-mail, Evernote ou Obsidian** como destino — a entrega é sempre no próprio chat.
