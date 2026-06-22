# Feature Specification: Quality & Compliance Optimization — 94% Target

**Feature Branch**: `007-quality-compliance-94pct`

**Created**: 2026-06-16

**Status**: Draft

**Input**: User description: "Continuidade do projeto — ler INSTRUCTIONS.md, usar GitNexus, analisar estado, planejar otimização até 94% compliance, FDC-U para decisões, corrigir não-conformidades da auditoria"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Correção de Testes Fracos com Validação Física (Priority: P1)

Como engenheiro de simulação, quero que os testes automatizados validem resultados contra benchmarks analíticos conhecidos (não apenas asserts genéricos de tipo), para garantir que o código produza resultados fisicamente corretos e detecte regressões numéricas.

**Why this priority**: FDC-U mostra O2 (validação física) como maior gap ponderado (0.0975). 55% do peso total está em O1+O2. Sem validação física, os testes não diferenciam código correto de código numericamente errado.

**Independent Test**: Pode ser testado rodando `pytest tests/test_benchmarks/` e verificando que cantilever_beam chega a PL³/(3EI) com erro < 5%, e plate_with_hole Kt converge para Kirsch (3.0).

**Acceptance Scenarios**:

1. **Given** um módulo de viga engastada com carga na ponta, **When** executo a simulação FEM e comparo com a solução analítica PL³/(3EI), **Then** o erro relativo deve ser < 5%
2. **Given** um módulo de placa com furo sob tração, **When** executo a simulação e calculo Kt (fator de concentração de tensão), **Then** o valor deve convergir para 3.0 (solução de Kirsch) com erro < 10% em malha refinada
3. **Given** um módulo de pressão de vento, **When** comparo com NBR 6123, **Then** os valores devem estar dentro de 10% para geometrias padronizadas

---

### User Story 2 - Resolução da Arquitetura Cross-Workspace (Priority: P1)

Como mantenedor do sistema, quero eliminar o workaround de `importlib` para importação entre instruments, substituindo por uma arquitetura de pacote instalável ou symlink estruturado, para que o sistema seja portável, testável em CI e não dependa de hacks de path.

**Why this priority**: O3 (arquitetura) é o segundo maior gap (0.0880). O importlib hack é frágil, quebra em mudanças de path, e impede CI/CD real.

**Independent Test**: Importar módulos de qualquer workspace sem `sys.path` manipulation e sem `importlib.util.spec_from_file_location`. Testar em ambiente limpo (sem variáveis de ambiente especiais).

**Acceptance Scenarios**:

1. **Given** uma instalação limpa do repositório, **When** executo `python -c "from physics_m3.composite import CompositeMaterial"`, **Then** a importação deve funcionar sem erros sem necessidade de PYTHONUTF8 ou manipulação de sys.path
2. **Given** os instruments physics-m3, cad-cae, kdi-m3, **When** qualquer um importa de outro, **Then** não deve usar `importlib` workaround
3. **Given** o código em CI, **When** executo o pipeline de testes completo, **Then** todas as importações cross-workspace funcionam sem configuração especial

---

### User Story 3 - Automação VVV Multi-Escala C11 (Priority: P2)

Como engenheiro de validação, quero que o VVV multi-escala (C11) seja automatizado via suite de testes, para garantir que simulações em macro, meso e micro escalas sejam verificadas consistentemente sem intervenção manual.

**Why this priority**: C11 é requisito explícito de INSTRUCTIONS.md. Atualmente a certificação é manual — risco de erro humano e inconsistência entre ciclos.

**Independent Test**: Executar `pytest tests/test_vvv_multiscale/` e verificar os 6 critérios de certificação automatizados (convergência de malha, estabilidade temporal, conservação, benchmark, cross-code, unidades).

**Acceptance Scenarios**:

1. **Given** um resultado de simulação em qualquer escala, **When** executo a suite VVV, **Then** a verificação cobre convergência de malha (<5% variação), estabilidade temporal (resíduo <1e-4), e conservação de massa/energia (<1% erro)
2. **Given** um resultado validado, **When** executo a certificação, **Then** recebo PASS/FAIL binário com os 6 critérios preenchidos e métricas de erro quantificadas
3. **Given** uma falha de validação, **When** a suite detecta, **Then** gera relatório apontando qual escala/domínio falhou e sugestão de retorno de fase (F5→F4/F3)

---

### User Story 4 - Portabilidade e CI/CD Readiness (Priority: P3)

Como DevOps do projeto, quero eliminar dependências de ambiente específico (PYTHONUTF8, sudo apt-get, CUDA version-locked) e ter um pipeline CI/CD funcional, para que novos contribuidores possam rodar o sistema sem configuração manual.

**Why this priority**: O4 (portabilidade) tem gap de 0.040. Sem CI/CD, não há garantia de regressão. As dependências de sistema impedem execução em GitHub Actions padrão.

**Independent Test**: Clonar repo em ambiente Ubuntu 22.04 limpo, executar `make setup && make test`, tudo passa sem sudo e sem PYTHONUTF8.

**Acceptance Scenarios**:

1. **Given** um ambiente Ubuntu 22.04 limpo sem CUDA, **When** executo `make setup`, **Then** todas as dependências Python são instaladas via pip/pipenv sem sudo e sem CUDA obrigatório (CPU fallback)
2. **Given** o mesmo ambiente, **When** executo `make test`, **Then** todos os testes que não exigem GPU passam sem variáveis de ambiente especiais
3. **Given** um push para main, **When** o CI executa, **Then** o pipeline completa em < 15 minutos com relatório de cobertura

### Edge Cases

- Módulos GPU-dependentes (CuPy) devem ter fallback para CPU com warning quando CUDA não está disponível
- Benchmarks analíticos com malha grossa podem ter erro > 5% esperado — documentar tolerância por benchmark
- Workspaces sem dependências externas devem ser testáveis independentemente
- Cross-workspace imports em ambiente CI limpo sem nenhuma configuração de path

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE implementar suite de benchmarks analíticos para validação física: cantilever beam (PL³/(3EI)), plate with hole (Kirsch Kt=3.0), wind pressure (NBR 6123)
- **FR-002**: Cada benchmark DEVE ter tolerância de erro documentada e assertiva quantitativa (não genérica)
- **FR-003**: Sistema DEVE substituir importlib workaround por estrutura de pacote instalável (pip install -e .) ou symlink gerenciado automaticamente
- **FR-004**: Sistema DEVE eliminar dependência de PYTHONUTF8 para operação básica
- **FR-005**: Sistema DEVE implementar suite VVV multi-escala (C11) automatizada com 6 critérios de certificação: convergência de malha, estabilidade temporal, conservação, benchmark, cross-code, unidades
- **FR-006**: VVV DEVE gerar relatório PASS/FAIL com métricas quantificadas e sugestão de retorno de fase
- **FR-007**: Sistema DEVE ter fallback CPU para módulos GPU-dependentes com warning explícito
- **FR-008**: CI pipeline DEVE executar suite completa em < 15 minutos
- **FR-009**: WAL patch_protocol DEVE ser atualizado para usar unified diff (git diff style) com validação de sintaxe
- **FR-010**: Mapa Único DEVE usar versionamento (Git LFS para dados binários, Git padrão para texto)
- **FR-011**: Sistema DEVE documentar dependências de sistema (CalculiX, libGLU) com fallback/documentação de instalação
- **FR-012**: Testes fracos com asserts genéricos (isinstance, is not None) DEVEM ser substituídos por asserts quantitativos com tolerância

### Key Entities *(include if feature involves data)*

- **BenchmarkAnalytic**: Definição de benchmark com solução analítica conhecida, tolerância de erro por refinamento de malha, método numérico esperado, domínio físico associado
- **VVVCertificate**: Resultado de certificação VVV com 6 critérios binários, métricas quantificadas (erro relativo, convergência, conservação), fase de retorno sugerida, timestamp
- **WorkspacePackage**: Definição de workspace como pacote instalável, com dependências, metadados de versão, compatibilidade cross-workspace
- **ComplianceReport**: Relatório de conformidade consolidado com score FDC-U por objetivo, não-conformidades abertas/fechadas, PQMS atual e tendência

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: FDC-U PQMS global do projeto sobe de 56.2% para ≥ 91.8% (gap de 35.5pp fechado)
- **SC-002**: 100% dos módulos com testes que validam física real contra benchmark analítico (não asserts genéricos)
- **SC-003**: Importação cross-workspace funciona sem importlib workaround em ambiente limpo
- **SC-004**: Suite de testes completa executa sem PYTHONUTF8 e sem sudo em ambiente Linux padrão
- **SC-005**: VVV multi-escala automatizado com certificação PASS/FAIL substitui verificação manual
- **SC-006**: CI pipeline executa em < 15 minutos com cobertura mínima de 80%
- **SC-007**: Zero não-conformidades abertas da auditoria após implementação (8 não-conformidades resolvidas)

## Assumptions

- O ambiente de desenvolvimento primário é Linux (Ubuntu 22.04+) — fallbacks para Windows/Mac são nice-to-have, não requisito
- GPU com CUDA 12.x está disponível para módulos que exigem aceleração, com fallback CPU funcional
- O repositório GitNexus permanece como ferramenta de code intelligence obrigatória (M3 da constituição)
- Projetos existentes (physics-m3, cad-cae, kdi-m3) são mantidos com sua estrutura atual — apenas a conexão entre eles é refatorada
- A ordem de implementação segue prioridade FDC-U: O2 (validação física) → O3 (arquitetura) → O1 (completude) → O4 (portabilidade) → O5 (documentação) → O6 (performance)
- Dependency on GitNexus CLI para análise de impacto pré-editorial em todas as modificações
