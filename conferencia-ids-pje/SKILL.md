---
name: conferencia-ids-pje
description: "Use ao pedir 'cheque os IDs' da peça contra os autos."
version: 1.0.0
author: Hermes Agent
license: MIT
category: legal
metadata:
  hermes:
    tags: [pje, ids, conferencia, processo, peca, mppe, verificacao]
    category: legal
    related_skills: [brazilian-legal-citation-integrity, parecer-recursal-civel-mppe, documento-intake-obsidian]
---

# Conferir os IDs do PJe citados numa peça contra os autos

Toda peça de 2º grau cita IDs (`ID 67106660` = petição inicial, `ID 67106699` = sentença,
`ID 67106700` = apelação). **ID citado não é ID verificado.** Esta skill entrega a conferência
**ID por ID** entre a peça (`.docx` do gabinete, PDF ou texto) e o extrato da consulta do processo
(`<NPU>-<id>-<id>-processo.pdf`, gerado pelo `ConsultaDocumento` do PJe) — offline e determinística,
sem login.

## When to Use / Quando usar

- O pedido é literalmente **`cheque os IDs em [<peça>] com os que constam em [<processo>]`** — a
  forma canônica, com os dois anexos no mesmo envio.
- Antes de **entregar parecer/manifestação de 2º grau** que cite IDs de peças dos autos: a conferência
  entra na revisão final, junto com a checagem de legislação/jurisprudência (essa é da skill
  `brazilian-legal-citation-integrity`, em turno e escopo próprios).
- Ao **arquivar a peça** no vault: a tabela `## IDs do PJe citados` da nota sai com a coluna
  `Confere?` preenchida, não com "pendente" (fluxo de arquivamento em `documento-intake-obsidian`).
- Quando a peça afirma um valor, data, prazo ou dispositivo "conforme ID X" e é preciso provar em que
  ID aquilo **de fato** aparece.

## O que a conferência entrega

1. **Veredito por ID** — o que a peça diz que o ID é × o que a consulta mostra (rótulo, tipo, data,
   assinatura) × o conteúdo lido nas páginas daquele ID.
2. **Achados transversais**, sempre separados em três categorias:
   - (a) **ID inexistente/incompatível** → erro, a peça não pode ir assim;
   - (b) **ID existente com rótulo impreciso** → ajuste de texto ("fatura" que os autos rotulam
     "boleto", plural para um documento único);
   - (c) **divergência de numeração** entre superfícies → nota, não erro.
3. **Imprecisão textual da própria peça** (ex.: relato dizendo "julgou parcialmente procedentes"
   quando o dispositivo literal diz "JULGO PROCEDENTES") — reporte **à parte do veredito dos IDs**.
4. **Documentos correlatos que a peça não citou** — inclusive o que ela aparentemente queria citar.

## Pipeline

1. **Achar os dois arquivos.** Anexo de Telegram cai em
   `~/.hermes/cache/documents/doc_<hash>_<nome original>` — o hash muda a cada reenvio, então busque
   por fragmento do NPU com `find ~ -maxdepth 8 -iname "*<fragmento>*"` (`search_files`/ripgrep pode
   falhar no home inteiro). Os dois arquivos do pedido chegam com o **mesmo mtime**.
2. **Rodar o script** (a parte mecânica):

```bash
python3 ~/.hermes/skills/legal/conferencia-ids-pje/scripts/conferir_ids_pje.py \
  --peca "<peca.docx>" --autos "<consulta>.pdf" \
  --valores "405,51" "664,44" "811,02" --out /tmp/conferencia.md
```

   Ele extrai a peça (`.docx` por `zipfile`, sem depender de `python-docx`) e os autos (PyMuPDF;
   cai para `pdftotext -layout`), parseia a **capa** (`Documentos / Id. / Data da Assinatura /
   Documento / Tipo`) nos dois layouts de extração, monta o **mapa página → ID** pelo rodapé
   `Num. <ID> - Pág. N`, lista os IDs citados, e reporta por ID: existência, rótulo/tipo/data,
   intervalo de páginas, ocorrências literais, signatário do rodapé e os documentos do mesmo lote
   que a peça não citou.
3. **Ler o texto, não só a tabela.** Autos de 300+ páginas são normais (~600 KB de texto): trabalhe
   sobre o arquivo salvo em disco, nunca sobre o retorno do terminal. Grave cópia do extrato e da peça
   em `~/.hermes/cache/scratch` para conferir sem re-extrair.
4. **Confirmar as âncoras fáticas dentro do intervalo de páginas do ID**: dispositivo citado entre
   aspas, valores, prazos, multas. A transcrição literal do `DISPOSITIVO` é o teste mais forte
   (o que a peça afirma que a sentença fixou × a letra do dispositivo).
5. **Contar ocorrências literais** dos valores que a peça afirma: valor que só aparece na peça da
   parte e ecoado na peça contrária **não tem correspondência nos autos** — afirmação verificável e
   frequentemente decisiva.
6. **Conferir a aritmética** ("o dobro da mensalidade de R$ 405,51") com o valor literal dos autos,
   nunca de cabeça.
7. **Relatar** na forma `ID | o que a peça diz | o que a consulta mostra | veredito`, e pedir a
   correção quando o achado for de texto.

## Regras e armadilhas

- **Há DUAS famílias de IDs no mesmo PDF, e nenhuma está errada.** A coluna `Id.` da capa e o cabeçalho
  `Num. <ID> - Pág. N` pertencem à instância em que a consulta foi feita; **as peças dentro dos autos
  citam a numeração do 1º grau** (a sentença aparece como `id. 250996456` na apelação e nas
  contrarrazões, enquanto a capa a lista com outro número). Diga sempre **qual superfície** foi
  conferida e entregue as duas ao usuário; nunca declare um ID "errado" sem isso.
- **Não converta entre as famílias pela ordem da lista.** As sequências **não são paralelas**: medido,
  o relatório de coparticipação citado na réplica como `id. 238159784` corresponde ao documento que a
  capa lista **dois** IDs à frente do que a ordem sugeriria. Ordem próxima entre IDs de um mesmo lote
  (todos juntados pela mesma parte no mesmo minuto) é coincidência de ingestão, não mapa. Para
  converter, compare **conteúdo** (total citado, competência, prestador).
- **Recomende citar o ID da consulta e, entre parênteses, o número usado pelas partes** ("sentença de
  ID <X>, referida pela recorrente como id. <Y>"): quem for conferir pelo número do recurso pode não
  achar o ID da capa, e vice-versa.
- **O rótulo que vale é o da coluna `Documento`, não o que a peça chama.** "faturas de IDs X e Y"
  quando Y é um **boleto** é imprecisão a apontar; o comprovante de pagamento costuma ser um ID
  **vizinho** que a peça não citou.
- **"relatórios de ID <X>" com um único ID é suspeito em dois sentidos:** o plural sem lista, e a
  escolha do ID. Liste os documentos parecidos do mesmo lote e verifique **qual deles carrega o total
  que a peça cita** — pode ser outro ID.
- **Leia TODAS as páginas do ID citado antes de dizer que ele não prova o que a peça afirma.** Um
  "Guia de custas recursais" pode trazer, dentro do **mesmo ID**, o boleto *e* o comprovante do
  pagamento bancário (data de efetivação, valor pago, pagador). Apontar ausência de comprovação de
  preparo sem percorrer as páginas do ID é falso positivo grave numa peça de admissibilidade.
- **Atos ordinatórios não são a intimação que a peça diz que faltou:** confira o **nome da peça** nos
  IDs vizinhos da data ("Intimação (Outros)" dirigida à parte contrária ≠ intimação da sentença).
- **O número grande no nome do arquivo da consulta (`<NPU>-<id>-<id>-processo.pdf`) não aparece no texto
  do PDF** — procurá-lo e obter `0` não significa processo errado: é o ID do documento de consulta de
  2º grau.
- **A conferência não se delega** (nem a `agy`/Antigravity nem a subagente): o valor está na leitura
  direta nos autos. O fechamento declara "sem delegação".

## Fechamento

- Abra dizendo **qual superfície** foi conferida (a capa da consulta × a numeração que as partes usam)
  e quantos IDs foram conferidos de quantos citados.
- Lista por ID com o veredito, depois os achados transversais nas três categorias — e, por último, as
  observações de redação da peça, separadas do veredito.
- Se algum ID citado não estiver na capa, diga **em qual superfície** ele aparece e quantas vezes no
  texto dos autos, em vez de chamá-lo de inexistente.
- Ofereça o próximo passo concreto (ajustar os IDs no `.docx`, preencher a coluna `Confere?` da nota do
  vault), sem executá-lo por conta própria quando o alvo é a peça do gabinete.

## Relacionadas

- `brazilian-legal-citation-integrity` — checagem de legislação/jurisprudência citada (turno e escopo
  próprios; reference `pje-ids-conferencia-autos.md` guarda a versão narrativa desta conferência).
- `parecer-recursal-civel-mppe` — elaboração/revisão do parecer de 2º grau (a conferência dos IDs é um
  dos itens da revisão final).
- `documento-intake-obsidian` — arquivamento da peça no vault com a tabela de IDs já conferida.
