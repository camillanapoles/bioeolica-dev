<!--
  Sync Impact Report — v2.6 → v2.7.0

  Version change: 2.6 → 2.7.0 (MINOR)
  Bump rationale: 4 new principles added (M1-M4), governance expanded

  Modified principles:
    - "Princípios Imutáveis" expanded from 6 to 10 rules
    - "Regras de Transição de Estado (FSM)" expanded with 3 new rules

  Added sections:
    - M1: Execução Singleton (Uma Task por Vez)
    - M2: Dependência Sequencial (Task → Task)
    - M3: GitNexus-First Analysis (Análise Obrigatória)
    - M4: Validação por Teste (não por presença de arquivo)

  Removed sections: Nenhuma

  Templates requiring updates:
    - plan-template.md: ✅ No changes needed — Constitution Check section already references "constitution file" generically
    - spec-template.md: ⚠️ Check if mandatory test-validation section needed
    - tasks-template.md: ⚠️ Check if M1/M2 constraint section needed

  Follow-up TODOs:
    - Nenhum — todos os placeholders preenchidos
-->

<!--
  Sync Impact Report — v2.7.0 → v2.7.1

  Version change: 2.7.0 → 2.7.1 (PATCH)
  Bump rationale: M4 expanded with pytest-per-task requirement

  Modified principles:
    - M4: Added pytest-per-task mandatory rule

  Added sections: Nenhuma
  Removed sections: Nenhuma

  Templates requiring updates:
    - tasks-template.md: ⚠️ Add pytest column or section
    - spec-template.md: ⚠️ Add testing requirements section

  Follow-up TODOs:
    - Migrar tests existentes para pytest formal por task
-->

# Project Constitution v2.7.1

## Princípios Imutáveis

- Fluxo obrigatório: SPECIFY → HUMAN_GATE → MAD → HUMAN_GATE → TASKS → EXECUTE → SELF_HEALING → DONE
- Estado sempre persistido em Git (.agent/)
- Contexto via GitNexus (nunca arquivos inteiros — CLI obrigatório)
- Human-in-the-Loop obrigatório em todos os gates
- Máximo 3 tentativas de self-healing por tarefa
- Definition of Done rigoroso

### M1 — Execução Singleton (Uma Task por Vez)

- **Uma task por turno.** Nunca planejar, iniciar ou verificar múltiplas tasks
  simultaneamente. Singleton obrigatório.
- **Cada task depende do sucesso da antecedente.** Se a task anterior falhou ou
  está incompleta, a próxima NÃO pode começar.
- **Verificação de sucesso obrigatória** antes de declarar qualquer task como
  completa ou avançar para a próxima.
- **Razão:** Tasks marcadas como DONE sem verificação produzem output não
  confiável. O custo de retrabalho aumenta 10× a cada fase pulada.

### M2 — Dependência Sequencial (Task → Task)

- A implementação DEVE ser uma task por vez — sequencial, não paralela.
- Nenhuma task pode ser iniciada sem que a antecedente tenha sido verificada
  e aprovada por TESTE (não por presença de arquivo).
- Tasks [P] (paralelas) só podem executar em paralelo APÓS verificação
  individual de cada uma — nunca antes.
- **Razão:** Dependências não-verificadas causam falhas em cascata que são
  difíceis de diagnosticar e caras de corrigir.

### M3 — GitNexus-First Analysis

- Antes de QUALQUER edição de código, DEVE rodar GitNexus CLI:
  `node .gitnexus/run.cjs query <symbol>` para verificar dependências.
- No início de cada sessão: `node .gitnexus/run.cjs analyze` para índice fresco.
- Mudança em função/classe/método REQUER `impact` analysis antes de editar.
- **Razão:** O usuário criou e configura o GitNexus CLI especificamente para
  análise de dependências. AGENTS.md torna obrigatório. O usuário verifica
  fisicamente a conformidade.

### M4 — Validação por Teste (não por presença de arquivo)

- **REIMPLEMENTAR CÓDIGO** significa código funcional e testado — NÃO
  significa arquivo presente no disco.
- Critério de sucesso de toda task: **teste bem-sucedido** (exit code 0,
  output esperado verificado, validação PASS).
- Arquivo presente sem teste que passe = task NÃO CONCLUÍDA.
- **Razão:** Múltiplas correções do usuário demonstraram que "arquivo presente"
  foi confundido com "implementação correta". O único critério aceito é
  validação por execução real.

## Regras de Transição de Estado (FSM)

- SPECIFY só avança após Y no gate
- MAD só avança após Y no gate
- EXECUTE só roda se human_approved_plan = true
- Tarefa só é DONE após Definition of Done + commit atômico
- Task DONE REQUER relatório de teste com evidência de PASS (M4)
- Transição entre fases REQUER HUMAN_GATE com aprovação explícita documentada
- Toda task DEVE ter issue correspondente no GitHub com estado sincronizado
  ao estado real de implementação (não ao tasks.md)
