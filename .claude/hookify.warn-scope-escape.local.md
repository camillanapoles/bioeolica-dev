---
name: warn-scope-escape
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: (^|/)(specs|src/cadreport|src/cad|src/crslr|workspace|instruments)/
---

## ⚠️ Possível FUGA DE ESCOPO (LAB-ENGINE)

Você está editando/criando um arquivo num escopo que **não pertence ao plano ativo** LAB-ENGINE (`Plans/peaceful-herding-otter.md`). Isso já aconteceu antes — o plano CAD+REPORT (`specs/012-cad-report`) foi confundido com o LAB-ENGINE.

### Escopos VÁLIDOS do LAB-ENGINE (edite apenas aqui)
`lab_engine/**` · `tests/lab_engine/**` · `alembic/**` · `Plans/**` · `docs/LAB-ENGINE-ARCHITECTURE.md` · `INSTRUCTIONS.md` · `pyproject.toml` · `CLAUDE.md` · `.claude/**`

### Escopos de OUTROS planos (FUGA)
- `specs/**` — ex: `specs/012-cad-report/` = pipeline CAD+REPORT (`src/cadreport/`).
- `src/cadreport`, `src/cad`, `src/crslr` — domínio legado, OUTRO escopo.
- `workspace/**` (singular) — projetos emergidos (motor-gerador-v1, pa-eolica-v3) = **FIXTURES** T12.
- `instruments/**` (plural) — ferramental de lab, OUTRO escopo.

### Antes de prosseguir
1. **PARE** e confirme: esta edição serve REALMENTE ao LAB-ENGINE?
2. Se for **T11** (migrar `lineage_db` de `workspace/`) ou **T12** (regenerar fixtures) — **justifique explicitamente** no contexto e siga.
3. Caso contrário, **NÃO prossiga** — é fuga de escopo. Informe o usuário.

> Esta regra é **complementar** (warn). O prompt-hook LLM (`scope-guard-prompt.txt`) julgará allow/deny contextualmente. Esta camada regex apenas emite o alerta antecipado, barato e determinístico.
