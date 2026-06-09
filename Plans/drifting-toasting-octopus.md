# PLANO: AVALIAÇÃO DA ENGINE + ARQUITETURA DO TIME MULTIDISCIPLINAR COM LABORATÓRIO VIRTUAL

## Contexto

Criamos a engine KDI/Omnibus v3.0-unified (PQMS 9.85/10) — um especificação formal de agente engenheiro-cientista multidisciplinar. O usuário agora quer utilizar esta engine **não como um agente único, mas como a fundação de um time completo de engenharia**: mecânicos, materiais, eletrotécnicos, fluidos, dinâmica — todos PhD, autores de livros, projetistas seniores, utilizando laboratório virtual, GitOps, dinâmica de reuniões, e publicando artigos científicos.

**Reqüisito central:** AVALIAR SE A ENGINE JÁ SUSTENTA A CONSTRUÇÃO DO TIME E DO LABORATÓRIO — e onde precisamos estender.

---

## 1. AVALIAÇÃO DA ENGINE vs. 6 REQUISITOS DO TIME

### R1: Time multidisciplinar de engenharia
| Engine tem | Engine não tem |
|---|---|
| KDI com identidade, 10 domínios, 7 capabilities, 5 níveis de proficiência | Perfil de agente único apenas — não há **especialização de papéis** (eng. mecânico ≠ eng. materiais ≠ fluidos) |
| M³ (macro-meso-micro) framework universal | Não há **alocação de tarefas** por especialidade |
| 7 métodos numéricos + decision tree | Não há **comunicação entre agentes** de diferentes especialidades |

**Veredito:** Engine sustenta a base teórica mas **não implementa** o time. Precisa de camada de orquestração multi-agente.

### R2: Laboratório virtual com ferramentas open source
| Engine tem | Engine não tem |
|---|---|
| M1 (Open Source First) com 50+ ferramentas mapeadas | Não há **workspace compartilhado** (dados, malhas, resultados acessíveis por múltiplos agentes) |
| M4 (Mapa Único) com estrutura de dados /data/ | Não há **isolamento de ambiente** por agente |
| M6 (RAG Knowledge) com fontes verificadas | Não há **versionamento de simulações** (quem rodou o quê, quando, com quais parâmetros) |

**Veredito:** Ferramentas mapeadas, mas sem workspace operacional. Precisa de especificação do laboratório virtual.

### R3: Dinâmica de reuniões e conversas em paralelo
| Engine tem | Engine não tem |
|---|---|
| F1 (Capturar Contexto) com Ishikawa + 5W1H | Não há **protocolo de reunião** (daily, revisão de projeto, pair programming) |
| F8 (Comunicar Resultados) com CRSLR | Não há **mecanismo de discussão** (agente A propõe, agente B critica, agente C valida) |
| M8 (Segurança) com checkpoints humanos | Não há **history de decisões** do time (atas, action items, deadlocks) |

**Veredito:** Engine tem comunicação estruturada mas não tem **dinâmica de grupo**. Precisa de protocolo de team dynamics.

### R4: Validação de modelos pela ciência (M3 VVV) ✅
| Engine tem | Engine não tem |
|---|---|
| M3 completo: Verificação → Validação → Certificação (6 critérios) | — |
| D3 Rigor (15% peso) com target 95% PASS em críticos | — |
| F5 return_conditions com 6 rotas + max_retries=3 | — |
| D7 Qualidade Numérica (precisão < 5%, convergência < 1%, fidelidade > 90%) | — |
| D9 Viés com checklist de 4 tipos + revisor hostil | — |

**Veredito:** **É o ponto mais forte da engine.** M3 VVV sustenta a validação científica. ✅✅✅

### R5: GitHub Workflow | GitOps
| Engine tem | Engine não tem |
|---|---|
| — | **Git não inicializado** no repositório |
| — | **Sem .github/workflows/** (zero pipelines) |
| M4 menciona Git LFS + DVC | Sem CI/CD para: validar WAL, rodar VVV automatizado, publish artigos |
| M5 Log 5W1H estruturado | Sem automação de deploy ou teste |

**Veredito:** **GAP CRÍTICO.** Engine exige computação → computação exige automação → automação não existe. Precisa de fundação GitOps completa.

### R6: Publicação de artigos científicos
| Engine tem | Engine não tem |
|---|---|
| Research-Paper-Writing Skill instalada (.claude/skill/) | Skill não está **integrada ao workflow** da engine |
| F8 (Comunicar) + M9 (Comunicação) com estrutura CRSLR | Sem **pipeline de submissão** (formatação, revisão, DOI, preprint) |
| D13 Inovação (2%) mede contribuições originais | Sem **template de paper** por domínio (CFD, FEM, materiais) |
| C11 Documentação (5%) | Sem **guia de estilo** para periódicos específicos |

**Veredito:** Skill existe mas não está integrada. Precisa de workflow F10 (Publicar) conectando engine → Research-Paper-Writing skill → repositório.

---

## 2. MAPA DE GAPS — O QUE PRECISA SER CONSTRUÍDO

| Gap | Requisito | Complexidade | Prioridade |
|-----|-----------|-------------|------------|
| **G1** Git não inicializado + sem .github/workflows/ | R5 GitOps | Média | **P0 — base de tudo** |
| **G2** Sem orquestração multi-agente (papéis, comunicação, alocação) | R1 Time | Alta | P1 |
| **G3** Sem workspace laboratório virtual (dados compartilhados, isolamento, versionamento) | R2 Lab | Média | P1 |
| **G4** Sem protocolo de team dynamics (reuniões, discussões, atas) | R3 Dinâmica | Média | P2 |
| **G5** Research-Paper-Writing skill não integrada ao workflow | R6 Artigos | Baixa | P2 |
| **G6** Sem pipeline de submissão acadêmica | R6 Artigos | Baixa | P3 |

---

## 3. PRINCÍPIO ARQUITETURAL: DOMÍNIOS ILIMITADOS — O PROCESSO DE SELEÇÃO É O INVARIANTE

> **ADENDO CRÍTICO:** A engine atual lista 10 domínios fixos. Para um projeto como sonda da NASA, 10 é insuficiente — seriam necessários domínios como: propulsão iônica, dinâmica orbital, radiação espacial, proteção térmica de reentrada, telecomunicações, ciência de instrumentos, etc.
>
> **A lista de 10 domínios é um EXEMPLO, não um limite.** O verdadeiro invariante é o **PROCESSO de seleção de domínios** — o método pelo qual se determina QUAIS domínios se aplicam a QUALQUER projeto.
>
> Isto materializa P1: "O método é o produto. O conteúdo é variável. O caminho é invariante."

### 3.1 Processo de Seleção de Domínios (O Invariante)

```
PARA CADA PROJETO:
──────────────────

PASSO 1 ── ANALISAR O PROBLEMA (F1)
  ├── Qual o fenômeno físico dominante?
  ├── Quais os subsistemas envolvidos?
  ├── Quais as restrições (físicas, normativas, ambientais, econômicas)?
  ├── Qual o ciclo de vida (extração → fabricação → operação → descarte)?
  └── Qual o ambiente de operação (Terra, espaço, subsolo, mar, vácuo, radiação)?

PASSO 2 ── IDENTIFICAR FAMÍLIAS DE DOMÍNIO
  ├── Família Mecânica: estruturas, dinâmica, vibrações, contato, fadiga, fratura
  ├── Família Fluidos: CFD, aerodinâmica, hidrodinâmica, multifásico, plasma
  ├── Família Materiais: metais, polímeros, cerâmicas, compósitos, semicondutores
  ├── Família Energia: termodinâmica, potência, conversão, armazenamento
  ├── Família Elétrica: circuitos, eletromagnetismo, motor/gerador, eletrônica
  ├── Família Construção: usinagem, soldagem, additive, montagem, tolerâncias
  ├── Família Ambiente: clima, corrosão, UV, vácuo, radiação, vibração ambiental
  ├── Família Normativa: ISO, ASTM, ASME, IEC, agências (NASA, ESA, ANATEL)
  ├── Família Econômica: LCC, ROI, TCO, viabilidade, risco financeiro
  ├── Família Controle: automação, sensores, atuadores, malha fechada, PID
  ├── Família Dados: aquisição, telemetria, processamento, incerteza, calibração
  ├── Família Software: embarcado, tempo real, criticalidade, verificação formal
  └── ⋮ (ilimitado — o processo permite adicionar qualquer família)

PASSO 3 ── APLICAR M³ EM CADA FAMÍLIA RELEVANTE
  ├── Macro: ambiente externo, sistema completo, fronteiras, stakeholders
  ├── Meso: subsistemas, interfaces, acoplamentos, trocas de energia/massa
  └── Micro: componentes, propriedades, microestrutura, fenômenos locais

PASSO 4 ── VALIDAR RELEVÂNCIA (relevance_check)
  ├── Pergunta binária: este domínio se aplica ao problema?
  ├── Se SIM → incluir na matriz de análise + gerar agente especialista
  ├── Se NÃO → documentar justificativa de exclusão
  └── Se INCERTO → investigar antes de decidir (P10 posture_unknown)

PASSO 5 ── DERIVAR O TIME DOS DOMÍNIOS CONFIRMADOS
  ├── Cada domínio SIM gera um ou mais agentes especialistas
  ├── A composição exata depende da complexidade (1 domínio pode ter 3 especialistas)
  └── Um sonda NASA exigiria 20-30 domínios → 20-30 agentes especialistas

PASSO 6 ── VERIFICAR COBERTURA
  ├── Nenhuma família foi ignorada sem justificativa?
  ├── O ciclo de vida completo do produto está coberto?
  └── As interconexões (matriz M³×M³) foram identificadas?
```

### 3.2 Isto resolve o problema da NASA

| Projeto | Domínios da lista fixa de 10 | Domínios via PROCESSO de seleção |
|---------|------------------------------|----------------------------------|
| Pá eólica | 8 de 10 se aplicam ✅ | 8 [mec,mat,flu,ener,amb,cons,eco,norm] ✅ |
| Motor-gerador | 7 de 10 se aplicam ✅ | 9 [+termo,+controle] ✅ |
| **Sonda NASA** | **3-4 de 10 se aplicam** ❌ | **20-30** [mec,mat,termo,flu,ener,elet, + propulsão iônica, dinâmica orbital, radiação, proteção térmica, telecom, instrumentos, software embarcado, controle térmico passivo, etc.] ✅✅✅ |

### 3.3 O que NÃO muda na engine com este princípio

- **Nada.** A engine já tem o framework P1 ("o método é o produto"), M¹ (busca de ferramentas), M³ (relevance_check), M⁴ (Mapa Único), F1-F9 workflow.
- **Apenas estendemos:** F2 (Mapear Domínios) ganha o processo de seleção acima — a lista fixa vira **exemplo**, e o **processo** vira o verdadeiro mecanismo de F2.
- **A engine permanece PQMS 9.85** — este adendo é uma instrução de USO, não uma correção na engine.

### 3.4 Concretização: Fluxo de Formação do Time

```
PROBLEMA (ex: "material para pá eólica")
  │
  ▼
F1 — CAPTURAR CONTEXTO (5W1H + Ishikawa + constraints)
  │
  ▼
F2 — MAPEAR DOMÍNIOS (aplicar Processo de Seleção → Passos 1-6)
  │  └── 10 domínios base + quantos mais forem necessários
  │
  ▼
COMPOSIÇÃO DO TIME (derivada dos domínios confirmados):
  ├── Agente Mecânica (proficiency 5 em estruturas, 4 em fadiga)
  ├── Agente Materiais (proficiency 5 em compósitos, 4 em degradação)
  ├── Agente Fluidos (proficiency 4 em aerodinâmica externa)
  ├── Agente Energia (proficiency 3 em efficiency analysis)
  ├── Agente Construção (proficiency 4 em manufatura de compósitos)
  ├── Agente Ambiente (proficiency 3 em degradação ambiental)
  ├── Agente Normativo (proficiency 4 em normas eólicas)
  ├── Agente Econômico (proficiency 3 em LCC)
  │
  └── Agente Coordenador (aloca, detecta dependências, convoca reuniões,
                           garante que 3+ trabalhem em paralelo sem bloqueio)
```

**REGRAS DE FORMAÇÃO DO TIME:**
1. **Domínio confirmado** → gera um agente especialista (pode ser o mesmo agente com múltiplos domínios se proficiency ≥ 3 em todos)
2. **Domínio rejeitado** → não gera agente, apenas registra justificativa no Domain_map
3. **Proficiência herdada** da engine base, com override por especialidade
4. **Coordenador** sempre presente — gerencia dependências, detecta deadlocks, convoca reuniões entre agentes que compartilham interconexão forte na matriz M³×M³
5. **Paralelismo mínimo:** 3 agentes trabalhando simultaneamente, cada um em seu domínio, sem bloquear os demais
6. **Sincronização:** agentes com interconexão forte sincronizam via reunião coordenada antes de avançar

---

## 4. ARQUITETURA PROPOSTA — PLATAFORMA

```
┌──────────────────────────────────────────────────────────────────────────┐
│              PLATAFORMA DE ENGENHARIA MULTI-AGENTE                       │
│              (TIME DERIVADO DO CONTEXTO → LAB CONFIGURADO POR PROJETO)   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │              WORKSPACE COMPUTACIONAL (LAB VIRTUAL)              │     │
│  │                                                                │     │
│  │  /workspace/{projeto}/                                         │     │
│  │  ├── context/               → F1: 5W1H, Ishikawa, constraints │     │
│  │  ├── domains/               → F2: relevance_check + M³        │     │
│  │  ├── team/                  → composição derivada do domínio   │     │
│  │  │   ├── coordinator/       → alocação, agenda, atas          │     │
│  │  │   ├── agent-materiais/   → ambiente isolado                │     │
│  │  │   ├── agent-mecanica/    → ambiente isolado                │     │
│  │  │   ├── agent-fluidos/     → ambiente isolado                │     │
│  │  │   └── ...                → conforme domínios relevantes     │     │
│  │  ├── shared/                → dados, malhas, resultados        │     │
│  │  ├── meetings/              → atas, decisões, deadlocks        │     │
│  │  ├── publications/          → papers em produção              │     │
│  │  └── vvv/                   → relatórios VVV, certificações   │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                    ↑ gerencia via GitOps                                │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │              GITOPS PIPELINE (.github/workflows/)               │     │
│  │  ├── validate-wal.yml    → valida logs WAL por PR              │     │
│  │  ├── vvv-automated.yml   → executa bateria VVV automática      │     │
│  │  ├── publish-paper.yml   → gera PDF + submit preprint          │     │
│  │  └── lab-sync.yml        → sincroniza workspace entre agentes  │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                    ↑ coordena + convoca                                │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │              ORQUESTRAÇÃO MULTI-AGENTE (derivada do contexto)   │     │
│  │                                                                │     │
│  │  Agente Coordenador (sempre presente):                         │     │
│  │  ├── Lê F1 → F2 → determina quais agentes convocar             │     │
│  │  ├── Aloca tarefas por domínio                                 │     │
│  │  ├── Detecta dependências (matriz M³×M³)                       │     │
│  │  ├── Agenda reuniões quando interconexão forte                 │     │
│  │  └── Resolve deadlocks (agente A espera resultado de B)        │     │
│  │                                                                │     │
│  │  Agentes Especialistas (convocados por domínio):               │     │
│  │  ├── Todos herdam a mesma engine (KDI/Omnibus v3.0)            │     │
│  │  ├── Cada um com proficiency override por especialidade        │     │
│  │  ├── Trabalham em paralelo em /workspace/agents/{papel}/       │     │
│  │  └── Sincronizam via shared/ + reuniões coordenadas            │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                    ↑ herdam (DNA comum)                                │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │  ENGINE KDI/OMNIBUS v3.0 (BASE INVARIANTE)  PQMS 9.85          │     │
│  │                                                                │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │     │
│  │  │PHILOSOPHY│→│   KDI    │→│ NUMERICAL│→│ DOMAINS  │         │     │
│  │  │  P1-P10  │ │Identity +│ │ Methods  │ │10 domains│         │     │
│  │  │  M³ +    │ │Capability│ │Decision  │ │ + M³ +   │         │     │
│  │  │ Posture  │ │Socratic  │ │Tree + GPU│ │Matrix M³ │         │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │     │
│  │       ↑                                        │                │     │
│  │       │   ┌──────────┐  ┌──────────┐  ┌──────────┐            │     │
│  │       └───│   WAL    │←─│ QUALITY  │←─│ MANDATES │            │     │
│  │           │  Memory   │  │ Metrics  │  │M1-M9 +   │            │     │
│  │           │ Log 5W1H  │  │PQMS 9.5  │  │Segurança │            │     │
│  │           └──────────┘  └──────────┘  └──────────┘            │     │
│  │                      ↑                                        │     │
│  │                 ┌──────────┐                                   │     │
│  │                 │ WORKFLOW │                                   │     │
│  │                 │ F1-F9    │                                   │     │
│  │                 │ VVV Loop │                                   │     │
│  │                 └──────────┘                                   │     │
│  └────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Camada 1: Engine KDI/Omnibus v3.0 — INVARIANTE (já existe, PQMS 9.85)
- A engine **não muda**. Ela é o DNA genético de CADA agente do time.
- Todo agente herda: identidade "Revisor Hostil Autônomo" + M³ + 7 métodos + 10 domínios + 9 mandatos + F1-F9 + WAL + quality_metrics.
- A engine é o que há de COMUM entre todos os projetos — "a busca" invariante.

### Camada 2: Orquestração Multi-Agente — DERIVADA DO CONTEXTO (a construir)
- **Agente Coordenador (sempre presente):** lê o problema (F1), executa relevance_check dos domínios (F2), DERIVA a composição do time a partir dos domínios SIM, aloca tarefas, gerencia dependências via matriz M³×M³, convoca reuniões quando interconexão forte, resolve deadlocks
- **Agentes Especialistas (convocados por demanda):** cada um com a mesma engine mas **proficiency override** (ex: Agente Materiais tem proficiency 5 em materials_science, 2 em fluid_dynamics)
- **Protocolo de Reunião:** quando 2+ agentes compartilham interconexão forte na matriz M³×M³ (ex: FSI = mecânica + fluidos), o coordenador convoca reunião. Formato: agente A apresenta → agente B critica como revisor hostil → coordenador valida → registra em ata
- **Isolamento:** cada agente escreve em `/workspace/{projeto}/agents/{papel}/` — nunca bloqueia outros agentes
- **Paralelismo:** agentes com domínios independentes (interconexão fraca ou nenhuma) trabalham simultaneamente sem coordenação

### Camada 3: GitOps Pipeline (a construir)
- `git init` + `.github/workflows/` com 4+ pipelines
- `validate-wal.yml`: valida JSON Schema de logs WAL em cada PR
- `vvv-automated.yml`: executa bateria VVV automatizada (convergência, conservação, benchmark)
- `publish-paper.yml`: gera PDF via Research-Paper-Writing skill + submit a preprint
- `lab-sync.yml`: sincroniza workspace entre agentes (shared/, meetings/, publications/)
- DVC para versionamento de dados grandes (malhas, resultados de simulação)

### Camada 4: Workspace Computacional / Lab Virtual (a construir)
- Estrutura de diretórios configurada por projeto (`/workspace/{projeto}/`)
- Agente isolado por diretório, dados compartilhados em `shared/` com controle de acesso
- Atas de reunião em `meetings/` com decisões e action items
- Versionamento de simulações: quem rodou o quê, com quais parâmetros, com quais resultados
- Relatórios VVV em `vvv/` com certificações

### Camada 5: Pipeline de Publicação Científica (a integrar)
- Workflow F10 (Publicar) como fase pós-F9: conecta resultado validado → Research-Paper-Writing skill → template de paper por domínio → PDF → preprint
- Template de paper por domínio (CFD, FEM, materiais, energia) com estrutura IMRaD
- CI/CD para gerar PDF, submeter a arXiv/engrXiv, registrar DOI
- M9 (Comunicação) estendido para incluir formato acadêmico

---

## 5. ENGENHARIA DE CONTEXTO — O SISTEMA NERVOSO DO TIME

> **AVALIAÇÃO CRÍTICA:** O plano até aqui trata da arquitetura (o esqueleto) mas NÃO trata da engenharia de contexto (o sistema nervoso). Um time de PhDs em paralelo SEM um protocolo de contexto robusto produz: agentes operando com dados desatualizados, conflitos não resolvidos, documentação sem indexação, e erros de informação que se propagam silenciosamente.

### 5.1 O que é Engenharia de Contexto neste sistema

Contexto é **todo dado, premissa, decisão, restrição, resultado e relação** que existe dentro de um projeto de engenharia. A engenharia de contexto é o conjunto de protocolos que garantem que este contexto:

1. **É capturado corretamente** na origem (sem perda, sem viés)
2. **Propaga-se fielmente** entre agentes (sem distorção, sem atraso crítico)
3. **Permanece consistente** entre agentes paralelos (sem conflito, sem stale data)
4. **É indexado e relacionável** (ontologia, taxonomia, classes, propriedades)
5. **É versionado e rastreável** (quem criou, quando, baseado em quê)
6. **Tem qualidade verificada** antes de ser usado por outro agente
7. **Tem ciclo de vida** (nasce, vive, envelhece, é arquivado ou refutado)

### 5.2 Avaliação do plano atual vs. Engenharia de Contexto

| Requisito de Contexto | O plano atual tem? | O que falta |
|----------------------|-------------------|-------------|
| **C1** Contexto centralizado indexado | ❌ Parcial — /workspace/{projeto}/context/ existe mas sem schema, sem ontologia, sem relacionamento de classes | Schema de contexto + grafo de conhecimento do projeto + taxonomia |
| **C2** Propagação de contexto entre agentes | ❌ Ausente — shared/ é um diretório, não um protocolo. Agente A atualiza dado, agente B não sabe | Protocolo publish/subscribe + eventos de mudança + notificação |
| **C3** Consistência de contexto paralelo | ❌ Ausente — 3 agentes lendo/escrevendo shared/ simultaneamente sem locks nem versões | Read/write locking + copy-on-write + detectores de conflito |
| **C4** Indexação com relacionamento de classes | ❌ Ausente — sem ontologia de engenharia, sem taxonomia, sem grafo | Ontologia OWL/RDF + grafo de conhecimento + query SPARQL |
| **C5** Versionamento de contexto entre agentes | ❌ Parcial — WAL versiona por agente mas não versão compartilhada do contexto do projeto | Context version tag + WAL cross-agent + changelog por conceito |
| **C6** Quality gate de contexto | ❌ Ausente — agente escreve em shared/ sem validação de que o contexto está completo e correto | Schema validation + sanity check + revisor hostil antes de publish |
| **C7** Resolução de conflitos de contexto | ❌ Ausente — se agente A usa fonte X e agente B usa fonte Y com valores diferentes, não há protocolo | Matriz de resolução: prioridade por fonte, por data, por autoridade |
| **C8** Decay de contexto (freshness) | ❌ Ausente — dado de 1990 tratado como igual a dado de 2025 | Freshness score + data de validade + trigger de re-validation |
| **C9** Rastreabilidade inter-agente | ❌ Parcial — WAL rastreia por agente, mas agente A → contexto → agente B não é rastreável | Context lineage: cada contexto carrega {criado_por, versão, baseado_em} |
| **C10** Garbage collection de contexto | ❌ Ausente — contexto órfão, substituído ou refutado nunca é limpo | GC policy: stale → archive → delete com retention |

### 5.3 O que precisa ser construído — Protocolo de Contexto

```
┌──────────────────────────────────────────────────────────────────────────┐
│                  SISTEMA DE CONTEXTO MULTI-AGENTE                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              1. SCHEMA DE CONTEXTO (ontologia)                   │    │
│  │                                                                  │    │
│  │  Material {                                                      │    │
│  │    id: UUID,                                                     │    │
│  │    class: "Compósito" | "Metal" | "Cerâmica" | "Polímero",      │    │
│  │    properties: {                                                 │    │
│  │      E: { value: 70, unit: "GPa", source: "ASTM D3039" },      │    │
│  │      σ_y: { value: 350, unit: "MPa", source: "ISO 527" },      │    │
│  │      ρ: { value: 1.8, unit: "g/cm³", source: "data_sheet" }    │    │
│  │    },                                                            │    │
│  │    relationships: { isUsedIn: ["pá_eólica_v3"],                  │    │
│  │                     hasSubclass: "Fibra-de-Vidro/Epóxi" },      │    │
│  │    lineage: { created_by: "agent-materiais",                     │    │
│  │              version: "1.2",                                     │    │
│  │              based_on: ["LOG-MATERIAIS-045"],                    │    │
│  │              freshness: 0.95 }                                   │    │
│  │  }                                                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              2. GRAFO DE CONHECIMENTO DO PROJETO                │    │
│  │                                                                  │    │
│  │  Projeto:PáEólicaV3                                              │    │
│  │    ├── hasAgent: Agent-Materiais, Agent-Mecanica, Agent-Fluidos │    │
│  │    ├── hasDomain: Materiais(5), Mecanica(4), Fluidos(3)         │    │
│  │    ├── hasMaterial: Compósito-Vidro/Epóxi [→ E=70GPa, ...]      │    │
│  │    ├── hasLoad: Carga-Vento [→ F=50kN, ciclo=S-N, ...]         │    │
│  │    ├── hasConstraint: IEC-61400 [→ safety_factor=1.5]          │    │
│  │    ├── hasMeeting: Reunião-FSI-001 [→ ata, decisões, ...]       │    │
│  │    └── hasPublication: Paper-CFDOtimizacaoPá [→ draft, ...]    │    │
│  │                                                                  │    │
│  │  (Relações entre nós: is_a, has_property, depends_on,            │    │
│  │   validates, contradicts, supersedes, based_on)                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              3. PROTOCOLO DE PROPAGAÇÃO                         │    │
│  │                                                                  │    │
│  │  Eventos:                                                        │    │
│  │  ├── context.updated(material_id, property, old_value, new_value)│    │
│  │  ├── context.deprecated(context_id, reason, replacement_id)      │    │
│  │  ├── context.conflict(agent_A, agent_B, context_id, diff)       │    │
│  │  └── context.published(agent_id, context_id, schema_validated)   │    │
│  │                                                                  │    │
│  │  Canais:                                                         │    │
│  │  ├── canal direto: agente → coordenador (urgente, blocking)      │    │
│  │  ├── canal publish/subscribe: shared/context/events.log          │    │
│  │  └── canal reunião: coordenador convoca afetados (interconexão)  │    │
│  │                                                                  │    │
│  │  Locking:                                                        │    │
│  │  ├── read: qualquer agente pode ler qualquer contexto a qqr momento │
│  │  ├── write: agente faz checkout do contexto → edita → commit     │    │
│  │  └── conflito: se 2 agentes checkout同一 contexto → merge necessário│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              4. QUALITY GATES DE CONTEXTO                       │    │
│  │                                                                  │    │
│  │  Antes de um contexto ser publicado em shared/:                  │    │
│  │                                                                  │    │
│  │  GATE 1 — Schema Validation: o contexto segue a ontologia?      │    │
│  │  ├── fields obrigatórios preenchidos?                            │    │
│  │  ├── tipos corretos? (E: number, unit: enum, source: string)    │    │
│  │  └── relationships válidas? (não referencia nó inexistente)      │    │
│  │                                                                  │    │
│  │  GATE 2 — Sanity Check: o contexto é fisicamente plausível?     │    │
│  │  ├── E=700 GPa para compósito? → FAIL (máx 150 GPa)             │    │
│  │  ├── σ_y=3500 MPa para alumínio? → FAIL (máx 700 MPa)           │    │
│  │  └── ρ=0.1 g/cm³ para metal? → FAIL (mín 1.5 g/cm³)            │    │
│  │                                                                  │    │
│  │  GATE 3 — Freshness Check: o contexto ainda é válido?           │    │
│  │  ├── data de criação < 12 meses? → PASS                         │    │
│  │  ├── 12-24 meses? → WARNING (marcar para revalidação)            │    │
│  │  └── > 24 meses? → FAIL (exigir revalidação antes de publicar)   │    │
│  │                                                                  │    │
│  │  GATE 4 — Revisor Hostil: outro agente valida o contexto        │    │
│  │  ├── agente A publica → coordenador designa agente B para revisar│    │
│  │  ├── agente B aplica P6 (Revisor Hostil) — busca contradições   │    │
│  │  └── se PASS → contexto liberado. Se FAIL → devolver para A     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              5. ÍNDICE DE CONTEXTO (busca + navegação)          │    │
│  │                                                                  │    │
│  │  /workspace/{projeto}/context/                                   │    │
│  │  ├── index.json           → árvore de todos os contextos        │    │
│  │  ├── ontology.json        → schema OWL simplificado             │    │
│  │  ├── graph.json           → grafo de conhecimento serializado   │    │
│  │  ├── materials/           → contextos de material               │    │
│  │  │   ├── compósito-vidro-epoxi.json                             │    │
│  │  │   └── aço-estrutural.json                                     │    │
│  │  ├── loads/               → contextos de carga                  │    │
│  │  ├── constraints/         → contextos de restrição              │    │
│  │  ├── methods/             → contextos de método numérico        │    │
│  │  ├── tools/               → contextos de ferramenta             │    │
│  │  ├── decisions/           → decisões de projeto registradas     │    │
│  │  └── lineage/             → linhagem de cada contexto           │    │
│  │                                                                  │    │
│  │  Queries suportadas:                                             │    │
│  │  ├── "qual material tem maior rigidez específica?" → query grafo│    │
│  │  ├── "quem decidiu o fator de segurança?" → query decisions/    │    │
│  │  ├── "qual contexto mudou da v1.0 para v1.1?" → query lineage/  │    │
│  │  └── "quais agentes usam este contexto?" → query graph反向      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              6. FLUXO DE CONTEXTO NO CICLO F1→F10               │    │
│  │                                                                  │    │
│  │  F1 ── Cria context/raiz: 5W1H + Ishikawa + constraints         │    │
│  │  F2 ── Cria context/domains: relevance_check + M³ por domínio    │    │
│  │  F3 ── Cria context/{domínio}/: análise de escala                │    │
│  │  F4 ── Cria context/tools + context/methods: seleção             │    │
│  │  F5 ── Quality gate: toda simulação deve publicar contexto VVV   │    │
│  │  F6 ── Documenta no WAL + atualiza grafo de conhecimento        │    │
│  │  F7 ── Contexto alimenta RAG                                     │    │
│  │  F8 ── Relatório CRSLR usa context/tree como fonte              │    │
│  │  F9 ── Arquivamento: contexto consolidado + lineage final       │    │
│  │  F10 ─ Paper usa context/ como fonte de dados e resultados       │    │
│  │                                                                  │    │
│  │  Fluxo inter-agente:                                             │    │
│  │  ┌────────────┐     ┌──────────────┐     ┌────────────┐        │    │
│  │  │ Material A │────→│ shared/      │←───→│ Mecânica B │        │    │
│  │  │ publica    │     │ context/     │     │ lê + usa   │        │    │
│  │  │ E=70GPa    │────→│ materiais/   │←───→│ para FEM   │        │    │
│  │  └────────────┘     └──────────────┘     └────────────┘        │    │
│  │       │                   │                      │               │    │
│  │       │         ┌─────────────────┐              │               │    │
│  │       └────────→│ quality gates   │←─────────────┘               │    │
│  │                 │ (schema+sanity+ │                               │    │
│  │                 │  freshness+     │                               │    │
│  │                 │  revisor hostil)│                               │    │
│  │                 └─────────────────┘                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Como este protocolo resolve os problemas de Context Engineering

| Problema | Como o protocolo resolve |
|----------|------------------------|
| **Agente A atualiza dado, B não sabe** | Evento `context.updated` publicado → B subscripto recebe notificação |
| **Agente A usa dado desatualizado de B** | Todo contexto tem `freshness` + data de criação. Se > 12 meses, WARNING |
| **Dois agentes editam mesmo contexto simultaneamente** | Checkout/commit + detecção de conflito + merge via coordenador |
| **Dado incorreto propaga para todo o time** | Quality gates (schema + sanity + freshness + revisor hostil) antes de publicar |
| **Decisão de projeto sem rastreabilidade** | `lineage: { created_by, version, based_on }` em todo contexto |
| **Documentação sem indexação** | `index.json` + `ontology.json` + `graph.json` — buscável e navegável |
| **Contexto contraditório entre fontes** | Resolução por prioridade: (1) peer-reviewed, (2) norma, (3) data sheet, (4) estimativa |
| **Contexto órfão ou refutado nunca limpo** | GC policy: stale (>12m sem uso) → archive → delete (30d em archive) |

### 5.5 Ontologia de Engenharia — Relacionamento de Classes

Para que o contexto seja indexável e relacionável por classe, precisamos de uma ontologia mínima:

```
Classe         Propriedades                        Relaciona-se com
──────────────────────────────────────────────────────────────────────
Material       {E, σ_y, σ_u, ρ, ν, α, k, ...}     isUsedIn → Component
Carga          {F, M, T, p, ciclo, frequência}     actsOn → Component
Componente     {geometria, massa, material}        hasMaterial → Material
Norma          {código, ano, organização}          governs → Domínio
Metodo         {tipo, precisão, custo}             appliesTo → Domínio
Ferramenta     {nome, versão, licença}             implements → Metodo
Decisão        {contexto, alternativa, rationale}  basedOn → Contexto
Simulacao      {parametros, resultados, VVV}       uses → Ferramenta
Publicação     {título, autores, DOI, status}      basedOn → Simulacao
Reunião        {pauta, ata, participantes}         resolves → Decisão
```

Cada instância destas classes é um **contexto** — e cada contexto tem:
- Schema validado (campos obrigatórios, tipos, enums)
- Lineage (quem criou, versão, baseado em quê)
- Freshness (data de criação + score)
- Relacionamentos (links para outros contextos no grafo)

### 5.6 O plano está completo de Engenharia de Contexto?

| O que deve ter | Tem? |
|---------------|------|
| Contexto centralizado e indexado por classe | ✅ Agora sim — ontologia + grafo + índice |
| Propagação entre agentes sem perda | ✅ Agora sim — eventos pub/sub + canais |
| Consistência em paralelo sem conflito | ✅ Agora sim — checkout/commit + merge + locking |
| Resolução de fontes contraditórias | ✅ Agora sim — matriz de prioridade por autoridade |
| Quality gate antes de propagar | ✅ Agora sim — 4 gates (schema+sanity+freshness+revisor) |
| Decay e freshness | ✅ Agora sim — freshness score + validade + re-validation |
| Rastreabilidade inter-agente | ✅ Agora sim — lineage com created_by + based_on |
| GC de contexto órfão | ✅ Agora sim — stale → archive → delete |
| Ontologia com classes e relacionamentos | ✅ Agora sim — 11 classes + propriedades + relações |
| Tudo indexado e buscável | ✅ Agora sim — index.json + graph.json + queries |

**Veredito final — Engenharia de Contexto: PRONTA.**

---

## 6. VERIFICAÇÃO

### Como verificar cada entrega:

| Entrega | Verificação |
|---------|-------------|
| Git inicializado | `git status` retorna árvore limpa |
| .github/workflows/ existe | `ls .github/workflows/` mostra 4+ YAMLs |
| Time derivado do contexto | Dar problema "material para pá eólica" → coordenador convoca agentes certos (materiais+mecânica+fluidos+...) e NÃO convoca eletricidade |
| Time mutante | Dar problema "motor-gerador" → coordenador convoca eletricidade+termo e NÃO convoca se irrelevante |
| 3 agentes em paralelo sem bloqueio | Agentes A e B escrevem em diretórios diferentes simultaneamente; nenhum espera o outro |
| Reunião funcional | 2 agentes com interconexão forte (ex: FSI) sincronizam via coordenador antes de prosseguir |
| **Contexto propagado** | Agente Materiais publica `E=70GPa` → Agente Mecânica recebe notificação automaticamente |
| **Quality gates ativos** | Publicar `E=700GPa` (fora do sanity check) → GATE 2 bloqueia com FAIL |
| **Ontologia funcional** | Query "qual material tem maior rigidez específica?" retorna resposta correta do grafo |
| **Lineage rastreável** | Dado → quem criou → quando → baseado em qual LOG WAL → tudo linkado |
| **Conflito detectado** | 2 agentes publicam valores diferentes para mesma propriedade → coordenador detecta e convoca resolução |
| Paper gerado | Research-Paper-Writing skill executada contra resultado de simulação → PDF |
| VVV automatizado | Pipeline CI/CD rejecta PR se validação falha (convergência, conservação, benchmark) |

### Critério de sucesso:
O time multi-agente (derivado do contexto) + laboratório virtual + GitOps + **engenharia de contexto** + publicação **opera um ciclo completo** (F1→F10) para **2 projetos fundamentalmente diferentes** (ex: pá eólica + motor-gerador) — cada um gerando time diferente, ontologia de contexto diferente, configuração de lab diferente, e saída publicável como paper com lineage rastreável até os dados brutos.

---

## 7. PRÓXIMOS PASSOS (Ordem de Execução)

| # | Ação | Entrega | Depende de |
|---|------|---------|------------|
| 1 | `git init` + `.gitignore` + `.github/` + README.md | Repositório Git + GitHub estrutura | — |
| 2 | Criar `.github/workflows/validate-wal.yml` e `lab-sync.yml` | CI/CD base | #1 |
| 3 | Criar especificação do workspace `/workspace/{projeto}/` com template de diretórios | Lab structure + template | #1 |
| 4 | Implementar **Schema de Contexto** (ontologia JSON + classes + propriedades + relacionamentos) | Ontologia de engenharia | #3 |
| 5 | Implementar **Grafo de Conhecimento** (index.json + graph.json + queries) | Context index | #4 |
| 6 | Implementar **Quality Gates de Contexto** (schema validation + sanity check + freshness + revisor hostil) | Context validation | #5 |
| 7 | Implementar **Protocolo de Propagação** (eventos pub/sub + locking checkout/commit + detecção de conflito) | Context sync | #6 |
| 8 | Implementar **Agente Coordenador**: lê F1→F2, DERIVA time dos domínios, aloca, gerencia dependências, convoca reuniões, gerencia contexto | Orquestração multi-agente | #7 |
| 9 | Implementar sistema de proficiency override (cada agente herda engine com override por especialidade) | Multi-agent KDI | #8 |
| 10 | Criar `.github/workflows/vvv-automated.yml` — pipeline que executa VVV em PR | CI/CD VVV | #1 |
| 11 | Criar `.github/workflows/publish-paper.yml` + integrar Research-Paper-Writing skill como F10 | Pipeline de publicação | #1 |
| 12 | Ciclo completo de teste F1→F10 com 2 projetos diferentes (pá eólica + motor-gerador) | Validação final | #2-#11 |
