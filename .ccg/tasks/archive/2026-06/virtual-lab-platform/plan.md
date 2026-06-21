# Plano de Implementação – Plataforma de Laboratórios Virtuais Computacionais Deep Tech

## Objetivo
Definir as etapas, arquitetura e divisão de trabalho para construir a plataforma de laboratórios virtuais, atendendo aos requisitos análise levantada na fase de análise.

## Premissas
- Complexidade L+, risco alto.
- Arquitetura baseada em micro‑serviços (ou módulos bem desacoplados) com banco de dados único.
- Linguagem de núcleo: Python (FastAPI) com SQLAlchemy/Pydantic para ORM.
- Solvers serão encapsulados em containers Docker e orquestrados via Celery com Redis broker (para MVP) ou Kubernetes para escalabilidade.
- Front‑end: React com TypeScript, Vite, e biblioteca de visualização VTK.js (@kitware/vtk.js).
- Banco de dados: PostgreSQL com extensão TimescaleDB para séries temporais.
- O modelo de dados será exposto como esquemas OpenAPI (JSON) para deixar claro que as chaves JSON representam as relações da orquestração.

## Restrições de Implementação
- Nenhum literal de configuração (URLs, credenciais, constantes físicas) pode aparecer diretamente no código‑fonte; todos devem ser fornecidos por variáveis de ambiente ou recuperados do banco de dados único.

## Etapas (Fases)

### Fase 1 – Arquitetura e Banco de Dados
1.1. Definir modelo de dados (entidades: Simulação, Parâmetro, Resultado, Material, SolverExecução, Publicação).  
1.2. Criar scripts de migração (Flyway/Liquibase).  
1.3. Implementar camada de acesso (DAO/Repositório) com unidade de trabalho.  
1.4. Configurar conexão, pool e testes de integração.  

### Fase 2 – Camada de Orquestração de Workflow
2.1. Escolher motor de workflow (Airflow básico, Celery ou Temporal).  
2.2. Definir DAG/tarefa genérica que recebe UUID de simulação e executa etapas: pré‑process → solver → pós‑process → validação → notificação.  
2.3. Criar adaptadores para cada tipo de solver (ex.: OpenFOAM, CalculiX, MFEM) que convertem entrada JSON → arquivo de caso → executa container → coleta saída.  
2.4. Gerenciamento de artifacts (arquivos de malha, resultados) em storage objetc (MinIO) ou sistema de arquivos compartilhado.  

### Fase 3 – API de Serviços (Back‑end)
3.1. Criar endpoints REST/GraphQL para:  
   - Criar/atualizar/listar simulações  
   - Iniciar/cancelar workflow  
   - Consultar status e resultados  
   - Gerar relatórios (PDF/Markdown)  
3.2. Implementar autenticação JWT e controle de acesso por papel.  
3.3. Testes de contrato ( Pact ou Postman collections).  
3.4. Documentação OpenAPI (Swagger UI).  

### Fase 4 – Front‑end (Portal do Laboratório)
4.1. Criar painel de visão geral (lista de simulações, filtros, status).  
4.2. Formulário de entrada de parâmetros com validação dinâmica baseada no schema do banco.  
4.3. Visualizador de resultados integrado (embed de ParaViewWeb ou componente VTK.js).  
4.4. Área de publicação: geração de manuscrito LaTeX a partir de metadados e download.  
4.5. Testes end‑to‑end (Cypress or Playwright).  

### Fase 5 – Integração e Validação
5.1. Rotina de carga de dados empíricos de validação (ex.: resultados de ensaios de tração, dados de túnel de vento).  
5.2. Implementar módulo de comparação que calcula RMSE, bias, etc.  
5.3. Gerar relatório de validação automático ao final de cada workflow.  
5.4. Pipeline de CI/CD (GitHub Actions) quebuild, testa e implanta em ambiente de staging.  
5.5. Incluir, como exemplo de validação, um caso concreto de análise de material (ex.: coupon de liga de titânio para estrutura de satélite) mostrando o caminho micro → meso → macro e a geração de relatório de resistência/fadiga.  

### Fase 6 – Documentação e Treinamento
6.1. Escrever guia de usuário (como criar uma simulação).  
6.2. Documentar API e extensão de solvers (como adicionar novo plugin).  
6.3. Realizar workshop interno com pilotos de domínio (energia, materiais, espaço).  

## Critérios de Aceite (por fase)
- Fase 1: Migrações aplicáveis, API de leitura/gravitação de parâmetros funcionando com testes >80% de cobertura.  
- Fase 2: Workflow dispara solvers de teste (ex.: script “hello world” que retorna JSON) e grava resultados no banco.  
- Fase 3: Endpoints respondem com códigos corretos, autenticação bloqueia acesso não autorizado.  
- Fase 4: Usuário consegue criar simulação, visualizar resultado e gerar relatório sem erros de console.  
- Fase 5: Relatório de validação mostra erro dentro de tolerância definida para caso de teste conhecido.  
- Fase 6: Documentação revisada e aprovada por pelo menos dois membros da equipe.

## Divisão de Tarefas (sugestão de equipes/roles)
- **Arquiteto de Dados**: Modelo de esquema, migrações, DAO.  
- **Engenheiro de Workflow**: Orquestração, adaptadores de solvers, gerenciamento de artifacts.  
- **Desenvolvedor Back‑end**: API, autenticação, documentación OpenAPI.  
- **Desenvolvedor Front‑end**: Portal, formulários, visualizador, publicação.  
- **QA/DevOps**: Testes, CI/CD, monitoramento, staging.  
- **Especialista de Domínio (por área)**: Validação com dados empíricos, revisão de modelos físicos.

## Estimativa de Esforço (aproximada)
| Fase | Effort (person‑days) |
|------|----------------------|
| 1 – Arquitetura e BD | 10 |
| 2 – Orquestração | 15 |
| 3 – API | 12 |
| 4 – Front‑end | 18 |
| 5 – Integração/Validação | 20 |
| 6 – Documentação/Treinamento | 8 |
| **Total** | **83 pd** (~4 meses com 2 pessoas full‑time, ou 2 meses com 4 pessoas). |

## Riscos e Mitigações
| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Solver licenciado faltando | Média | Alto | Usar apenas solvers open‑source no MVP; deixar interface aberta para plugins comerciais futuros. |
| Performance de I/O de grandes campos | Baixa | Alto | Armazenar resultados em storage de objetos; usar compressão (HDF5/ZFP). |
| Dificuldade de visualização web de grandes datasets | Média | Médio | Implementar nível de detalhe (LOD) e streaming de tiles. |
| Falta de padronização de unidades | Baixa | Médio | Adotar SI universalmente; validar entrada no front‑end. |
| Atraso na obtenção de dados empíricos | Média | Médio | Utilizar datasets públicos abertos inicialmente; laterais com parceiros. |

## Próximos Passos Imediatos
1. Revisar este plano com a arquiteta de dados e líder de equipe.  
2. Definir stack tecnológico final (linguagem, orchestrator, banco).  
3. Criar repositório Git para a plataforma (se ainda não existir) e definir branch de desenvolvimento.  
4. Inicializar o projeto com estrutura de diretórios (backend/, frontend/, infra/, docs/).  

---
*Plano elaborado em 21/06/2026, com base na análise de requisitos realizada na fase anterior.*
