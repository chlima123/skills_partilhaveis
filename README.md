# Skills Compartilháveis

Coleção de skills de agente (Hermes / agentes de IA) para instalação em qualquer agente.

## Instalar no Hermes

Copie a pasta da skill para `~/.hermes/skills/`:

```bash
SKILL=pesquisa-jurisprudencial-ia
git clone https://github.com/chlima123/skills_partilhaveis /tmp/skills_partilhaveis
cp -R "/tmp/skills_partilhaveis/$SKILL" ~/.hermes/skills/
```

## Skills

| Skill | Descrição |
|---|---|
| [apple-design](apple-design/) | Abordagem da Apple para design de interface e movimento fluido/físico, traduzida para a web (gestos, springs, momentum, materiais translúcidos, tipografia, reduced-motion). |
| [analise-processo-6-prompts](analise-processo-6-prompts/) | Análise de processo extenso por IA em 6 etapas encadeadas (MAPEAR → DECOMPOR → CRUZAR → COMPARAR → TESTAR → AUDITAR), com relatório executivo auditado. Inclui script `analise_processo_ia.sh`. |
| [pesquisa-jurisprudencial-ia](pesquisa-jurisprudencial-ia/) | Pesquisa jurisprudencial com IA usando os 6 prompts, com o relatório publicado diretamente no chat. |
