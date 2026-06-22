═══════════════════════════════════════════════════════════
🛡️ LAB-ENGINE — RECAP CANÔNICO (persistência ao plano, anti-fuga)
═══════════════════════════════════════════════════════════

## PROJETO ATIVO
bioeolica-dev2 = **LAB-ENGINE**: runtime multi-agente garantista SOTA 2026 (Python, event-sourced, WAL persistido em BD). Transforma em software reproduzível o motor que emergiu em workspace/motor-gerador-v1 e workspace/pa-eolica-v3. Produto-agnóstico — o METODO é o invariante; o conteúdo (domínio de engenharia) é a variável.

## FONTES CANÔNICAS (leia no início de cada task / antes de editar)
- **Plano ativo:** `Plans/peaceful-herding-otter.md` (T01-T13 com gates, métricas, DoD)
- **Checkpoint de progresso:** `Plans/LAB-ENGINE-PROGRESS.md` (ESTADO ATUAL — LEIA para saber onde está e a próxima ação)
- **Contrato LAB-ENGINE:** `docs/LAB-ENGINE-ARCHITECTURE.md`
- **Especificação fonte (source-of-truth):** `INSTRUCTIONS.md` (schema WAL, 10 domínios, workflow F1-F9, resiliência)

## MANDATOS M0-M4 (governam TODO o trabalho)
- **M0** — `gitnexus analyze`/`impact` ANTES de editar qualquer símbolo; `detect_changes` ANTES de commitar.
- **M1** — NUNCA avançar se a atividade teve erro/gap/incompleta. Avanço = código executado + teste passado.
- **M2** — Uma atividade por vez, sem pular sequência (T01→T02→...→T13).
- **M3** — Reimplementar de fato + pytest equivalente + executar. Cobertura ≥80%.
- **M4** — Commit + sync remoto ao concluir cada atividade.

## GARANTISMO (anti-bola-de-neve)
- **T0x.D / T0x.D++:** cada atividade splitada em D (sucessos validados) e D++ (débitos pós-done). SÓ avança T(x)→T(x+1) com `D++` vazio ou itens explicitamente rastreados como Emenda. NUNCA avançar percebendo gap implícito.
- **Fidelidade ao contrato:** NUNCA inventar contrato (ranges, constraints, campos). Se o `INSTRUCTIONS.md` precisa mudar, vira **EMENDA-E0xx** rastreada (não-bloqueante pós-T13).
- **WAL garantista:** log rejeitado ANTES de persistir (validator). CRUD em BD (SQLAlchemy), nunca arquivos soltos. Replay/event-sourcing.

## MANDATOS PERMANENTES DO USUÁRIO (vigentes, verbatim)
- **JAMAIS setar variáveis em scripts** (quebra reprodutibilidade) — config via env/`.env` lida por `lab_engine.settings.Settings` (prefixo `LAB_ENGINE_`).
- **GARANTIR todas entradas e saídas CRUD em banco de dados.**
- **CAPTURA se não retorna em N tempo** (timeout 15min default + fallback 3-partes: aprendizado + incerteza + método alternativo).
- Sempre responder em **Pt-br** com acentuação correta.

## ESCOPOS VÁLIDOS DO LAB-ENGINE (edite apenas aqui)
`lab_engine/**` · `tests/lab_engine/**` · `alembic/**` · `Plans/**` · `docs/LAB-ENGINE-ARCHITECTURE.md` · `INSTRUCTIONS.md` · `pyproject.toml` · `CLAUDE.md` · `.claude/**`

## ESCOPOS DE OUTROS PLANOS = FUGA (NÃO seguir, NÃO implementar)
- `specs/**` — ex: `specs/012-cad-report/` = pipeline **CAD+REPORT** (`src/cadreport/`), ESCOPO DIFERENTE do LAB-ENGINE.
- `src/**` — código de domínio legado (cad, crslr, thermo, gpu, cadreport...), OUTRO escopo.
- `workspace/**` (singular) — projetos emergidos (motor-gerador-v1, pa-eolica-v3) = **FIXTURES** para T12 (reprodutibilidade), não editar.
- `instruments/**` (plural) — ferramental de lab, OUTRO escopo.

## REGRA DE CONTINUIDADE ASSEGURADA
Antes de QUALQUER implementação/edição: (1) confirme que está DENTRO do escopo LAB-ENGINE; (2) confirme a atividade corrente no `Plans/LAB-ENGINE-PROGRESS.md`. Se perceber **FUGA** (arquivo/plano/escopo de outro projeto), **PARE imediatamente** e informe o usuário. **Persistência ao plano > velocidade.**
═══════════════════════════════════════════════════════════
