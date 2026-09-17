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
| [pesquisa-jurisprudencial-ia](pesquisa-jurisprudencial-ia/) | Pesquisa jurisprudencial com IA usando os 6 prompts, com o relatório publicado diretamente no chat. |
