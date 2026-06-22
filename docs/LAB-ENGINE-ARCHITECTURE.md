# LAB-ENGINE — Arquitetura Canônica

> **Source of truth do runtime multi-agente garantista SOTA 2026.**
> Contrato derivado e fiel a `INSTRUCTIONS.md` (KDI Omnibus Engine v3.0). Cada atividade T02–T13 do plano `Plans/peaceful-herding-otter.md` implementa uma seção deste documento.
>
> **Status:** CONTRATO APROVADO (T01). Implementação inicia em T02.

---

## 1. Visão — O que é o LAB-ENGINE

O LAB-ENGINE é o **runtime Python-nativo, event-sourced e garantista** que transforma em software reproduzível o que emergiu empiricamente em `workspace/motor-gerador-v1` (29 contextos, 7 agentes) e `workspace/pa-eolica-v3` (25 contextos).

Ele é **produto-agnóstico por construção** (`INSTRUCTIONS.md:701-729`): não nasce para um produto, mas para **qualquer produto** de engenharia envolvendo os 10 domínios. O **caminho** (filosofia → KDI → métodos → domínios → mandatos → fluxo → métricas → WAL) é **invariante**; o **conteúdo** (geometrias, materiais, normas) é **variável**.

> *"O CAMINHO É INVARIANTE. O CONTEÚDO É VARIÁVEL."* — `INSTRUCTIONS.md:729`

O produto final não é um agente estático — é o **loop de autogeração**: agentes que se auto-criam aplicando a mesma metodologia que os define (`CLAUDE.md`: "O Metodo é o Produto").

---

## 2. Princípios Fundamentais

| Princípio | Enunciado | Fonte |
|---|---|---|
| **Produto-agnóstico** | 10 domínios + workflow F1-F9 + métricas D1-D13 idênticos entre produtos; só o conteúdo muda | `INSTRUCTIONS.md:701-729` |
| **Source of truth = WAL em BD** | Cada ação = um log WAL persistido em banco. Sem log, não há memória; sem memória, não há aprendizado | `INSTRUCTIONS.md:2128-2131` |
| **Garantismo schema-enforced** | Log é **rejeitado antes de persistir** se violar o JSON Schema (draft 2020-12) | `INSTRUCTIONS.md:2198-2267` |
| **Zero-hardcoded (12-factor)** | Config via `pydantic-settings` (env + `config.toml`); **PROIBIDO** definir variáveis em scripts — quebra reprodutibilidade | Mandato do usuário + M0 |
| **Toda E/S CRUD em BD** | Nenhuma I/O de WAL em arquivos soltos; tudo via repository + SQLAlchemy | Mandato do usuário |
| **Resiliência com captura por timeout** | Agente que não retorna em N tempo é capturado + fallback registrado + workflow não trava | Mandato do usuário + `INSTRUCTIONS.md:644-649` |

---

## 3. Mandatos Operacionais (governam TODO o desenvolvimento)

| ID | Mandato | Aplicação no LAB-ENGINE |
|---|---|---|
| **M0** | `gitnexus analyze` + `impact` **antes** de editar qualquer símbolo | Cada atividade começa com M0 |
| **M1** | **Nunca** avançar se a atividade teve erro/ficou incompleta/não validada. Avanço = código executado + teste passado | Cadeia T01→T13 com gate de bloqueio |
| **M2** | Uma atividade por vez, sem pular sequência | `addBlockedBy` entre tarefas |
| **M3** | Reimplementar de fato + gerar **pytest equivalente** + executar | TDD + cobertura ≥80% por atividade |
| **M4** | Commit + sync remoto ao concluir cada atividade | Gate final de cada T |

> Mandatos de domínio **M1–M9** do `INSTRUCTIONS.md` (M1=busca SOTA, M3=VVV, M8=risco S1/S2, M9=comunicação reguladora...) são **conteúdo** executado pelos agentes em runtime — não confundir com os mandatos operacionais M0–M4 acima, que governam o **desenvolvimento** do engine.

---

## 4. WAL Protocol — Source of Truth Garantista

### 4.1 Estrutura do log (`INSTRUCTIONS.md:2132-2196`)

```
log_id        : LOG-[UUID v4]
timestamp     : { created, started, finished }  — ISO 8601
5w1h          : { what, why, who, when, where, how }
map_index     : { project, domain, scale, task, parent_log, child_logs }
validation    : { status, method, reference, error_metrics }
quality_metrics : D1_completude ... D10_ensino
next_steps, rag_sources, patches
```

### 4.2 JSON Schema (draft 2020-12) — válidoção **antes** de persistir

Campos **obrigatórios** (top-level): `["log_id", "timestamp", "5w1h", "map_index", "validation"]`

Restrições-chave (espelhadas 1:1 em Pydantic v2 na T02):

| Campo | Restrição |
|---|---|
| `log_id` | pattern `^LOG-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$` (UUID v4) |
| `timestamp` | `{created, started, finished}` date-time; `additionalProperties: false` |
| `5w1h.what` | string, **minLength 10** |
| `5w1h.why` | string, **minLength 10** |
| `5w1h.where` | requer `file`, `version` |
| `5w1h.how` | requer `method`, `tool`, `tool_version` |
| `map_index.project` | pattern `^PRODUTO-` (formato `PRODUTO-[NOME]-[VERSAO]`) |
| `map_index.domain` | enum dos **10 domínios** (§5) |
| `map_index.scale` | enum `["macro", "meso", "micro"]` |
| `map_index.task` | pattern `^TASK-` |
| `validation.status` | enum `["PASS", "FAIL", "PENDING"]` |

**Garantismo:** o `validator` (T04) rejeita qualquer log que viole estas restrições **antes** de chegar ao `store` (T03). Nenhum log inválido entra no BD — este é o invariante fundamental do engine.

### 4.3 Auditoria (`INSTRUCTIONS.md` anomalias L2005/L2006)

O `auditor` (T04) detecta e relata:
- `PENDING` há mais de 24h (log nunca validado)
- órfãos de `parent_log` (referência a log inexistente)
- breaches de schema (logs que escaparam da validação — não deve ocorrer)

---

## 5. Os 10 Domínios (conteúdo variável, estrutura invariante)

Enum canônico de `map_index.domain` (`INSTRUCTIONS.md:2260`):

```
mecanica · fluidos · termo · energia · eletricidade
materiais · construcao · ambiente · normativo · economico
```

Cada domínio é instanciável via `domain_template` (`INSTRUCTIONS.md:731-758`): `subdomains`, `relevance_check` (binário), `m3` (macro/meso/micro), `methods` (dos 7: FEM/MPM/SPH/DEM/Peridynamics/ROM+PINNs/híbridos), `tools` (open source SOTA).

O `agent-factory` (T08) lê a config declarativa de domínios e **deriva** o time de agentes com proficiência — sem variáveis hardcoded.

---

## 6. Workflow F1–F9 (FSM com guards)

Workflow canônico (`INSTRUCTIONS.md`: 9 fases). Implementado como máquina de estados finita persistida por projeto (T06):

```
F1 problem_statement → F2 ... → F4 decision_tree (seleciona métodos)
   → F5 validação (return_conditions volta a F3 se falha) → ... → F8 comunicar → F9 fechar
```

**Invariante FSM:** transição bloqueada se o `guard` (`return_conditions`) falha; o estado sobrevive a restart (persistido em BD, não em memória). Cada fase tem `return_conditions` que retorna à fase correta em caso de falha de validação (ex.: F5 → F3 se falha validação aeroelástica).

---

## 7. Resiliência — Captura por Timeout + Fallback

Contrato exato (`INSTRUCTIONS.md:644-650`):

```
timeout: { max_iterations: 5, max_recursion: 3, timeout_minutes: 15,
           saturation: "3 iterações consecutivas sem novo insight →
                        consolidar parciais + declarar incerteza explícita",
           fallback: "(a) relatar o que aprendeu,
                      (b) relatar o que não determinou,
                      (c) propor método alternativo (analítico/experimental/humano)" }
```

Implementação (T07 `resilience.py`):
- **Retry + backoff exponencial** (`max_iterations`, `max_recursion`)
- **Timeout configurável** (default 15 min) — agente excedido é **capturado** + workflow não trava
- **Fallback 3-partes** registrado no WAL (aprendido + incerteza + alternativo)
- **Circuit breaker** — abre após falhas consecutivas, curto-circuita chamadas
- **Dead-letter WAL** — logs de ações irrecuperáveis não se perdem
- **Saga compensation** (`INSTRUCTIONS.md` L644-649, L965-968) — desfaz efeitos de transação parcial

---

## 8. A2A + Zero-Hardcoded

### A2A (Agent-to-Agent) — T08

Padrão Google A2A via contracts Pydantic: `input`/`output`, `correlation_id`, `reply_to`. Agent registry. Agentes reagem por subscription a eventos WAL.

### Zero-Hardcoded (12-factor) — T11

- **Config:** `pydantic-settings` lê env + `config.toml`; paths relativos
- **Lint gate:** PROÍBE `${HOME}` literal, paths absolutos, valores hardcoded em qualquer script/config
- **Migração:** `lineage_db.json` existentes (2 formatos: array `entries` vs dict top-level) → formato WAL canônico via script idempotente

---

## 9. Mapeamento Atividades → Componentes

| Atividade | Componente | Seção deste contrato |
|---|---|---|
| T01 | rename `workspaces/`→`instruments/` + **esta doc** | (done) |
| T02 | `lab_engine/wal/models.py` — Pydantic do schema | §4.2 |
| T03 | `lab_engine/wal/store.py` + Alembic — CRUD/BD | §4 |
| T04 | `lab_engine/wal/{validator,auditor}.py` — garantismo | §4.2-4.3 |
| T05 | `lab_engine/runtime/bus.py` — command bus + event store | §6 (eventos) |
| T06 | `lab_engine/runtime/workflow.py` — FSM F1-F9 | §6 |
| T07 | `lab_engine/runtime/resilience.py` | §7 |
| T08 | `lab_engine/agents/` — A2A + agent-factory declarativo | §5, §8 |
| T09 | `lab_engine/api/` — FastAPI CRUD+commands | (interface) |
| T10 | `lab_engine/cli.py` — Typer `lab-engine` | (interface) |
| T11 | lint gate zero-hardcoded + migração `lineage_db` | §8 |
| T12 | prova de reprodutibilidade (regenera 2 projetos) | §1 (goal) |
| T13 | cobertura 80% + property-based + security + sync | §3 M3/M4 |

---

## 10. Stack

| Camada | Tecnologia |
|---|---|
| Linguagem / gestor | Python ≥3.11 · `uv` |
| Persistência | SQLAlchemy 2.0 + Alembic (SQLite local; Postgres pronto) |
| Schema/garantismo | Pydantic v2 + pydantic-settings |
| API | FastAPI (OpenAPI) |
| CLI | Typer (`lab-engine`) |
| Testes | pytest + pytest-asyncio + hypothesis (property-based) |
| Logging | structlog |
| Workflow engine | event-sourcing custom leve (reproduzível, TDD-friendly); *upgrade path*: Temporal |

---

## 11. Verificação do Produto Pronto

1. `uv run pytest --cov=lab_engine --cov-fail-under=80` → verde
2. `uv run lab-engine new demo --domains "Mecânica,Fluidos"` → cria projeto + deriva time + WAL em BD
3. Log WAL inválido → **rejeitado** pelo validator (teste negativo)
4. Agente que excede 15 min → capturado + fallback registrado + workflow não trava
5. `lab-engine run` → regera `motor-gerador-v1` e `pa-eolica-v3` com ≥90% de match estrutural
6. `lab-engine audit` → relatório sem órfãos/PENDING>24h
7. Lint gate reprova qualquer `${HOME}`/hardcoded; 0 refs a `workspaces/`
8. `uv run uvicorn lab_engine.api:app` → OpenAPI em `/docs`

---

*Este documento é o contrato. Implementações (T02–T13) são consideradas corretas somente se cumprem este contrato + passam nos gates ECC/CCG de cada atividade.*
