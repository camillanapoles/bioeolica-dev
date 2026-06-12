# Project Constitution v2.6

## Princípios Imutáveis
- Fluxo obrigatório: SPECIFY → HUMAN_GATE → MAD → HUMAN_GATE → TASKS → EXECUTE → SELF_HEALING → DONE
- Estado sempre persistido em Git (.agent/)
- Contexto via GitNexus MCP (nunca arquivos inteiros)
- Human-in-the-Loop obrigatório em todos os gates
- Máximo 3 tentativas de self-healing por tarefa
- Definition of Done rigoroso

## Regras de Transição de Estado (FSM)
- SPECIFY só avança após Y no gate
- MAD só avança após Y no gate
- EXECUTE só roda se human_approved_plan = true
- Tarefa só é DONE após Definition of Done + commit atômico
