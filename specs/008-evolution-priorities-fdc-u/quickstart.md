# Quickstart — Spec 008 Evolution Priorities (Fase 0)

> Validação rápida da Fase 0: C7 (DB unify + pyproject) + C3 (specs 002/006)

## Pré-requisitos

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,test]"
```

## C7 — Unificação DBs

```bash
# Dry-run: verificar o que seria migrado
python scripts/migrate_unify_db.py --dry-run

# Executar migração real (com backup automático)
python scripts/migrate_unify_db.py

# Verificar resultado
python scripts/audit_deps.py --check
```

**Saída esperada:**
- `data/bioeolica.db` é a única DB com dados
- `./bioeolica.db` e `data/database.db` removidos ou viram symlink
- `pyproject.toml` com `[project.dependencies]` populado

## C7 — Dependências pyproject

```bash
# Auditar dependências declaradas vs imports reais
python scripts/audit_deps.py --check

# Verificar instalação limpa
pip install -e ".[dev,test]"
pytest --co -q  # lista de descoberta sem executar
```

**Saída esperada:**
- Zero `ModuleNotFoundError`
- `pip install -e .` succeeds
- `pytest` descobre todos os testes

## C3 — Spec 002 TopOpt

```bash
# Validar spec revisada
pytest tests/ -k "topopt" --co -q   # list discovery

# Se implementação existir, validar convergência
pytest tests/ -k "topopt" -v --tb=short
```

**Saída esperada:**
- Tests descobertos e PASS (se implementados)
- Escopo OpenMDAO/Dakota documentado

## C3 — Spec 006 Validação Experimental

```bash
# Validar protocolos mapeados
pytest tests/validation/ -v --tb=short --junitxml=reports/vvv-006.xml

# Verificar 6 critérios VVV
pytest tests/validation/ -k "certification" -v
```

**Saída esperada:**
- 6/6 protocolos PASS
- Todos os 6 critérios VVV atendidos
- Relatório JUnit gerado em `reports/vvv-006.xml`

## Verificação de Integridade

```bash
# Status do repo pós-migração
git status
git diff --stat

# Se tudo OK, commitar Fase 0
git add -A && git commit -m "008 Fase 0: DB unify + spec 002/006 revision"
```

## Rollback

```bash
# Se migração falhar, restaurar backup
ls data/backup/
python scripts/migrate_unify_db.py --restore data/backup/<snapshot>
```
