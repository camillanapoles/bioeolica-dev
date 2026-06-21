# PLANO: ANÁLISE DE PADRÕES & PROCESSOS + ANTIDESVIO + OTIMIZAÇÃO SGNODTICS

---

## CONTEXTO

O documento `INSTRUCTIONS.md` (~58K tokens) contém o Engine Omnibus v3.0 completo — um sistema de 8 partes integradas para o agente `mech-electro-materials-scientist`. O usuário requer:

1. **Mapeamento exaustivo dos padrões e processos** contidos no documento — O QUE são, COMO funcionam, ONDE se aplicam
2. **Mecanismo de antidesvio** — como GARANTIR que a execução não desvie dos padrões estabelecidos (anti-odr = anti-desvio-de-rota)
3. **Otimização da estrutura SGNODTICS** — construção e refinamento do meta-sistema que une todos os padrões

**SGNODTICS** = Sistema de Gestão Normativa para Otimização Determinística Iterativa Contínua Socrática (inferido do contexto do Engine: Socrático, Gestão, Normas, Otimização, Determinação, Iteração, Contínuo, Socrático). O termo representa o meta-padrão invariante que costura as 8 partes do Engine.

---

## 1. MAPEAMENTO DOS PADRÕES (O QUE, COMO, ONDE)

### 1.1 Padrões Filosóficos (P1-P10)

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| P1: The Way By Content | Método invariante, conteúdo variável | Ciclo invariante de 8 partes | Todo o Engine — estrutura central |
| P2: Holismo Exaustivo | Pensar, refletir, investigar holisticamente | M³ + exaustão com relevância | F1-F9, Domain_map, M7 |
| P3: Cobertura 75-90% | Critério de limite com % conforme relevância | Verificação de cobertura por domínio | F2, M7, D1 |
| P4: Ensinar a Pescar | Auto-instrução, nunca resposta pronta | 6 passos socráticos + 15 perguntas auto-reflexão | KDI socratic_behavior, response_structure |
| P5: Agente Autônomo | Agente decide, instrutor catalisa | Checkpoints humanos em F1/F4/F5/F8 | F1/F4/F5/F8, P10 |
| P6: Revisor Hostil | Validar como inimigo da qualidade | Auto-validação + verificação independente | M3, D3, D9, F5 return_conditions |
| P7: Contexto Antes de Ação | 5W1H + Ishikawa antes de agir | F1 process steps 1-5 obrigatórios | F1 input + process |
| P8: Open Source First | Ferramentas open source SOTA | M1 processo 6 passos + validação | M1, tools em todos domains |
| P9: Sustentabilidade e Ética | Ciclo de vida + segurança + ética | M8 com FMEA/HAZOP + DEC ética | M8, D8 impacto |
| P10: Colaboração Humana | Autonomia + checkpoints humanos | 4 checkpoints obrigatórios + override | F1/F4/F5/F8, human_interface |

### 1.2 Padrões KDI

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| 5 Níveis de Proficiência | Awareness → Operational → Proficient → Advanced → Expert | Auto-avaliação + evidências | kdi.core_capabilities.proficiency_framework |
| 8 Regras Socráticas | Nunca limitar, sempre fundamentar | Consequências progressivas (advertência→bloqueio) | kdi.socratic_behavior |
| 6 Passos de Resposta | Validação→Fundamentação→Metodologia→Execução→Validação→Extensão | Sequência fixa, não pula etapas | kdi.socratic_behavior.response_structure |
| Auto-Instrução Contextual | 8 perguntas socráticas + depth_control | 5 max_iterations, 3 max_recursion, 15min timeout | kdi.context_engine |
| 5 Métodos de Incerteza | Monte Carlo, Interval Analysis, Perturbation, Bayesian, Expert | Sempre reportar nominal ± IC 95% | kdi.output_standards.uncertainty_methods |

### 1.3 Padrões de Métodos Numéricos

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| Árvore de Decisão Binária | Deformação <10%? → FEM. 10-100%? → MPM/SPH. >100%? → MPM/SPH. Fratura? → Peridynamics/DEM | Nós binários encadeados, 5+ níveis | numerical_methods.decision_tree |
| Tabela Comparativa 11 Critérios | Ranking por critério (ex: small_deformation: FEM > MPM > SPH...) | 11 critérios × 6 métodos = 66 rankings | numerical_methods.comparison_table |
| 7 Métodos + Híbridos + Coupling | FEM/MPM/SPH/DEM/Peridynamics/ROM+PINNs/Híbridos | Cada método com 8-12 atributos | numerical_methods.methods |
| Validação Experimental por Método | FEM→DIC, MPM→column collapse, SPH→dam break, DEM→angle of repose | Benchmark específico + cross-code | numerical_methods.experimental_validation |
| GPU Guidance por Método | SPH > MPM > DEM > Peridynamics > FEM (ganho GPU) | Recomendação específica | numerical_methods.gpu_guidance |

### 1.4 Padrões de Domínios

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| 10 Domínios Fixos | mecânica, fluidos, termo, energia, eletricidade, materiais, construção, ambiente, normativo, econômico | Relevance_check binário obrigatório | domains.* |
| M³ em Cada Domínio | Macro (sistema), Meso (interface), Micro (componente) | 3-5 elementos por escala | domains.*.m3 |
| Template de Novo Domínio | structure + rules + verificação | 6 regras obrigatórias | agnosticism.domain_template |
| Matriz de Interconexão M³×M³ | 19 pares críticos com 3 escalas cada | forte→MOOSE, fraco→preCICE, serial→workflow | m3_interconnection_matrix |

### 1.5 Padrões de Mandatos (M1-M9)

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| M1: Trigger + Processo + Output + Log | Toda ação tem gatilho, passos, saída, registro | 6 passos executáveis + validação | mandates.M1-M9 |
| M2: Árvore de Decisão de Coupling | preCICE (particionado) vs MOOSE (monolítico) | Binária: códigos independentes? → acoplamento fraco? | mandates.M2 |
| M3: VVV em 3 Níveis | Verificação → Validação → Certificação (6 critérios binários) | Se QUALQUER critério falha → FAIL | mandates.M3 |
| M8: Segurança S1/S2/S3 | S1→FMEA(RPN>200), S2→checklist 10 itens, S3→padrão | Classificar risco antes de prosseguir | mandates.M8 |
| M9: CRSLR | Contexto→Resultados→Síntese→Limitações→Recomendações | Audiência primeiro, incerteza sempre | mandates.M9 |

### 1.6 Padrões de Fluxo (F1-F9)

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| Trigger + Input + Process + Output + Next + Mandato | Cada fase tem 6+ elementos | Estrutura invariante | workflow.F1-F9 |
| F1 Input Schema Validado | Required + optional + validation | 4 campos obrigatórios, 3 opcionais | workflow.F1.input |
| F4 Decision Criteria | method_selection + tool_selection + coupling_decision + fallback | 4 critérios com árvore de decisão | workflow.F4.decision_criteria |
| F5 Return Conditions | 5 rotas de retorno + max_retries=3 | Cada rota retorna a fase específica | workflow.F5.return_conditions |
| F8 CRSLR + Revisão Hostil | Contexto→Resultados→Síntese→Limitações→Recomendações | Incluir incerteza, auto-revisão | workflow.F8 |
| F9 Encerramento Verificado | Integridade + arquivamento + knowledge graph + PQMS | 6 passos obrigatórios | workflow.F9 |

### 1.7 Padrões de Qualidade (D1-D13)

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| Dimensão = Pergunta + Métrica + Target + Verificação | 4 atributos obrigatórios por D | Alvo PQMS 9.5 | quality_metrics.D1-D13 |
| Weight Table com Críticos | 13 dimensões com pesos + domínios críticos + razões | Σ(Peso_i × Nota_i) | quality_metrics.weight_table |
| Loop Kaizen Contínuo | Medir → Gap → Patch → Re-medir | A cada 3 ciclos F1-F9 | quality_metrics.loop_kaizen |

### 1.8 Padrões WAL

| Padrão | O Que | Como | Onde |
|--------|-------|------|------|
| Log 5W1H + Map Index + Validation | Estrutura de 15+ campos | JSON Schema validado | wal_protocol |
| Patch Atômico com Rollback | Snapshot pré-patch → diff → validação → rollback | Snapshot antes de escrever | wal_protocol.patch_protocol |
| Encriptação 4 Níveis | public/internal/confidential/restricted | AES-256-GCM + envelope KMS | wal_protocol.encryption_security |

---

## 2. MECANISMO DE ANTIDESVIO (Anti-Odr)

### 2.1 Detectores de Desvio

| # | Detector | O Que Detecta | Como Atua | Trigger |
|---|----------|---------------|-----------|---------|
| AD1 | Desvio de Fase | Fase executada sem trigger, input incompleto, output sem next | Validação JSON Schema pré-fase + pós-fase | Cada transição Fn→Fn+1 |
| AD2 | Desvio de Escala | Escala M³ pulada sem justificativa | Verificação coverage_checklist na F3 | F3 step_5 + F5 return |
| AD3 | Desvio de Método | Método escolhido sem passar pela decision_tree | Validação contra numerical_methods.decision_tree | F4 step_2 |
| AD4 | Desvio de VVV | Resultado reportado sem certificação VVV PASS | Bloqueio de F5→F6 sem PASS | F5 step_4 → F6 |
| AD5 | Desvio de Mandato | Ação executada sem log M5, sem trigger Mx | Validação WAL pós-ação | Cada tool call |
| AD6 | Desvio de Cobertura | Cobertura <75% sem justificativa | Verificação D1 no F2 | F2 step_3 |
| AD7 | Desvio de Quantidade | Limitação artificial de itens (ex: "liste 3") | Detecção de padrões "N itens" na resposta | Pós-resposta, KDI rule 2 |
| AD8 | Desvio de Resposta Socrática | Resposta sem fundamentação teórica (pula step_1/step_2) | Verificação de estrutura 6-passos | Resposta gerada |
| AD9 | Desvio de Ferramenta | Ferramenta sugerida sem fonte real verificada | Verificação M1 step_1-3 | Toda recomendação de tool |
| AD10 | Desvio de Segurança | S1/S2 sem FMEA/checklist antes de prosseguir | Bloqueio M8 step_1 antes da análise | M8 trigger |
| AD11 | Desvio de Retorno Máximo | max_retries=3 excedido no mesmo retorno | ESCALAÇÃO → parar → notificar | F5 return_conditions |
| AD12 | Desvio de Acoplamento | Acoplamento forte configurado como fraco sem justificativa | Verificação contra m3_interconnection_matrix | M2 step_3 |

### 2.2 Barreiras de Desvio (Pontos de Bloqueio)

| Ponto | Barreira | O Que Bloqueia | Como Remove |
|-------|----------|---------------|-------------|
| **G1** | F1 input validation | Prosseguir sem problem_statement, available_data, constraints | Preencher required fields |
| **G2** | F2 coverage gate | Prosseguir sem relevance_check para os 10 domínios | Completar Domain_map |
| **G3** | F3 scale gate | Pular escala M³ sem justificativa | Documentar justificativa no Scale_analysis |
| **G4** | F4 method gate | Selecionar método sem decision_tree | Executar decision_tree |
| **G5** | F5 certification gate | Reportar sem VVV PASS | Obter certificação 6/6 critérios |
| **G6** | F6 log gate | Salvar sem log M5 completo | Completar log WAL |
| **G7** | F8 communication gate | Comunicar sem CRSLR + incerteza | Estruturar relatório |
| **G8** | F9 close gate | Encerrar sem integridade verificada | Executar F9 step_1 |
| **G9** | M8 safety gate | Prosseguir S1 sem FMEA | Executar FMEA RPN |
| **G10** | M3 six-criteria gate | PASS sem 6/6 critérios de certificação | Preencher todos |

### 2.3 Protocolo de Correção de Desvio

```
DESVIO DETECTADO → REGISTRAR (ADn + Fase + Contexto)
↓
CLASSIFICAR GRAVIDADE:
  - CRITICAL (S1, max_retries, desvio de segurança) → PARAR + NOTIFICAR
  - ALTA (desvio de VVV, desvio de método) → BLOQUEAR FASE + OBRIGAR CORREÇÃO
  - MÉDIA (desvio de cobertura, desvio de quantidade) → WARNING + CORREÇÃO OPCIONAL
  - BAIXA (desvio de log, desvio de formato) → LOG + CORREÇÃO ASSINCRONA
↓
APLICAR CORREÇÃO:
  - Se CRITICAL: escalar para usuário com RCA
  - Se ALTA: reverter ao gate anterior, reexecutar com AD visível
  - Se MÉDIA: sugerir correção, registrar no WAL como PENDING
  - Se BAIXA: registrar no WAL como WARNING, correção no próximo ciclo
↓
VERIFICAR CORREÇÃO:
  - Re-aplicar detector ADn
  - Se PASS → liberar
  - Se FAIL novamente → escalar gravidade
```

---

## 3. OTIMIZAÇÃO DA ESTRUTURA SGNODTICS

### 3.1 Arquitetura SGNODTICS (Meta-Padrão)

```
SGNODTICS = Sistema de Gestão Normativa para Otimização Determinística Iterativa Contínua Socrática

┌──────────────────────────────────────────────────────────────────────┐
│                       SGNODTICS META-PADRÃO                           │
│  O padrão que gerencia todos os padrões — meta-sistema invariante    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  S — Socrático:       Auto-instrução, perguntas, reflexão            │
│  G — Gestão:          Mandatos M1-M9 gerenciam a execução            │
│  N — Normativo:       10 domínios + normas + compliance              │
│  O — Otimização:      PQMS 9.5, kaizen, D1-D13, loop contínuo       │
│  D — Determinístico:  Árvores de decisão, critérios binários         │
│  T — Técnico:         7 métodos numéricos, 5 níveis proficiência     │
│  I — Iterativo:       F1-F9 cíclico, VVV returns, kaizen loop       │
│  C — Contínuo:        WAL→filosofia, conhecimento→RAG, melhoria     │
│  S — Sistêmico:       8 partes conectadas em ciclo fechado           │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Otimizações Propostas

| # | Otimização | Parte SGNODTICS | O Que Muda | Impacto |
|---|-----------|-----------------|------------|---------|
| OP1 | Automatizar detectores AD1-AD12 como hooks | G + S | Scripts/sh de validação pré/pós fase | Bloqueia desvios em tempo real |
| OP2 | Criar checklist consolidado de G1-G10 | G | Template markdown validável por JSON | Gate único verificável |
| OP3 | Adicionar métrica de antidesvio no PQMS (D14) | O | Nova dimensão: AD_pass_rate = % detectores PASS/total | PQMS → 9.5+ |
| OP4 | Centralizar todos os padrões em um meta-documento | S | Extrair padrões do INSTRUCTIONS.md para /patterns/master.md | Única fonte de verdade de padrões |
| OP5 | Template de Domain_map pré-formatado | N | Markdown com 10 domínios + relevance_check + M³ + justificativa | Reduz desvio de cobertura (AD6) |
| OP6 | WAL validator script | I | Script que valida log contra JSON Schema antes de persistir | Bloqueia desvio AD5 |
| OP7 | Decision_tree executor | D | CLI/script que guia a árvore binária interativamente | Garante AD3 |
| OP8 | Template CRSLR | C | Template markdown com campos obrigatórios + placeholders | Garante AD8, reforça G7 |
| OP9 | Mapa de correlação padrão→detector→gate | S | Matriz completa: cada padrão linkado a seu AD e Gate | Rastreabilidade de desvio |
| OP10 | Scorecard SGNODTICS por ciclo | O | Relatório automático ao final de F9: % aderência a cada padrão | Visibilidade de desvio acumulado |

### 3.3 Plano de Implementação

```
FASE 1 — IMEDIATA (prioridade máxima)
├── OP5: Template Domain_map (reduz desvio de cobertura F2)
├── OP8: Template CRSLR (reforça comunicação F8)
├── OP2: Checklist G1-G10 (gate único verificável)
└── OP9: Mapa padrão→detector→gate (rastreabilidade)

FASE 2 — CURTO PRAZO
├── OP6: WAL validator script (bloqueia log sem validação)
├── OP7: Decision_tree executor (garante método correto)
└── OP1: Hooks AD1-AD12 (automatiza detecção)

FASE 3 — MÉDIO PRAZO
├── OP3: D14 Antidesvio no PQMS (métrica contínua)
├── OP4: Meta-documento de padrões (fonte única)
└── OP10: Scorecard SGNODTICS por ciclo (visibilidade)
```

---

## 4. VERIFICAÇÃO

| O Que Verificar | Como | Critério |
|----------------|------|----------|
| Mapa de padrões completo | Cross-check contra INSTRUCTIONS.md | 100% dos padrões do doc mapeados |
| Detectores AD1-AD12 implementáveis | Verificar se cada detector tem trigger + ação + resolução | 12/12 operacionais |
| Barreiras G1-G10 | Cada gate tem condição de bloqueio + remoção | 10/10 com ambos |
| Otimizações OP1-OP10 | Cada proposta tem parte SGNODTICS + mudança + impacto | 10/10 completas |
| Plano executável | Fases têm ordem clara, dependências, prioridade | F1→F2→F3 sem ciclos |
