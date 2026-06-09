#!/usr/bin/env bash
# criar-workspace.sh
# Instancia o template de workspace para um novo projeto de engenharia.
# Uso: ./scripts/criar-workspace.sh nome-do-projeto
#
# Exemplo:
#   ./scripts/criar-workspace.sh pa-eolica-v3
#   Cria workspace/pa-eolica-v3/ com estrutura completa de diretórios

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$REPO_DIR/workspace/template"
WORKSPACE_DIR="$REPO_DIR/workspace"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── Validação ─────────────────────────────────────────────────────────────

if [ $# -lt 1 ]; then
    echo -e "${RED}ERRO: informe o nome do projeto.${NC}"
    echo "Uso: ./scripts/criar-workspace.sh nome-do-projeto"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="$WORKSPACE_DIR/$PROJECT_NAME"

# Valida nome do projeto (apenas letras, números, hífens e underscores)
if ! [[ "$PROJECT_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo -e "${RED}ERRO: nome do projeto inválido. Use apenas letras, números, hífens e underscores.${NC}"
    exit 1
fi

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${RED}ERRO: o diretório $PROJECT_DIR já existe.${NC}"
    echo "Remova-o ou escolha outro nome."
    exit 1
fi

# ─── Instanciação ──────────────────────────────────────────────────────────

echo -e "${CYAN}Criando workspace para: ${YELLOW}$PROJECT_NAME${NC}"

# Verifica se o template existe
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo -e "${RED}ERRO: template não encontrado em $TEMPLATE_DIR${NC}"
    echo "Certifique-se de que o template existe antes de criar projetos."
    exit 1
fi

# Copia o template
cp -r "$TEMPLATE_DIR" "$PROJECT_DIR"
echo -e "${GREEN}✓${NC} Estrutura copiada para $PROJECT_DIR"

# Remove arquivos .gitkeep do template (não devem constar no projeto real)
find "$PROJECT_DIR" -name '.gitkeep' -delete

# ─── Cria arquivos de placeholder ──────────────────────────────────────────

# context/
cat > "$PROJECT_DIR/context/problem_statement.md" <<- EOF
# Declaração do Problema — $PROJECT_NAME

## Descrição

<!-- Descreva o fenômeno, sistema ou falha a analisar -->

## Objetivo

<!-- Defina o objetivo quantitativo -->

## Dados Disponíveis

<!-- Geometria, materiais, cargas, dados experimentais -->

## Restrições

<!-- Normas, prazos, orçamento -->
EOF

cat > "$PROJECT_DIR/context/5w1h.json" <<- EOF
{
  "project": "$PROJECT_NAME",
  "what": "",
  "why": "",
  "who": "",
  "when": "",
  "where": "",
  "how": "",
  "how_much": ""
}
EOF

# domains/
cat > "$PROJECT_DIR/domains/relevance_check.md" <<- EOF
# Relevance Check — $PROJECT_NAME

| Domínio | Aplica? | Justificativa |
|---------|---------|---------------|
| Mecânica | | |
| Fluidos | | |
| Termodinâmica | | |
| Energia | | |
| Eletricidade | | |
| Materiais | | |
| Construção | | |
| Ambiente | | |
| Normativo | | |
| Econômico | | |
EOF

# team/coordinator/
cat > "$PROJECT_DIR/team/coordinator/team-composition.md" <<- EOF
# Composição do Time — $PROJECT_NAME

## Domínios Confirmados

| Domínio | Agente | Proficiência |
|---------|--------|--------------|

## Alocação de Tarefas

| Tarefa | Responsável | Prazo | Depende de |
|--------|-------------|-------|------------|

## Reuniões

| # | Data | Pauta | Participantes | Status |
|---|------|-------|--------------|--------|
EOF

# shared/
cat > "$PROJECT_DIR/shared/README.md" <<- EOF
# Dados Compartilhados — $PROJECT_NAME

Este diretório contém dados compartilhados entre todos os agentes do projeto.

## Estrutura

- \`materials/\` — Banco de dados de materiais e propriedades
- \`geometry/\` — Modelos CAD, malhas, geometrias de referência
- \`loads/\` — Condições de carga e contorno
- \`results/\` — Resultados consolidados de simulações

## Regras

1. Dados em \`shared/\` são **read-only** para agentes (exceto o agente que os publicou)
2. Toda publicação em \`shared/\' deve passar pelos Quality Gates de Contexto
3. Versionamento via Git LFS para arquivos > 1MB
4. Nunca editar o dado de outro agente — comunicar via coordenador se houver conflito
EOF

# meetings/
cat > "$PROJECT_DIR/meetings/decision_log.md" <<- EOF
# Registro de Decisões — $PROJECT_NAME

| # | Data | Decisão | Contexto | Responsável | Aprovado por |
|---|------|---------|----------|-------------|--------------|
EOF

# vvv/
cat > "$PROJECT_DIR/vvv/certification/status.md" <<- EOF
# Certificação VVV — $PROJECT_NAME

| Análise | Verificação | Validação | Certificação | Data |
|---------|-------------|-----------|-------------|------|
EOF

# publications/
cat > "$PROJECT_DIR/publications/README.md" <<- EOF
# Publicações — $PROJECT_NAME

Artigos científicos gerados a partir das análises deste projeto.

## Fluxo

1. Resultado validado (VVV PASS) → rascunho em \`drafts/\`
2. Revisão pelo time → figuras em \`figures/\`
3. Submissão a preprint/periódico → arquivos em \`submissions/\`

## Papers

| Título | Autores | Status | Submetido em |
|--------|---------|--------|-------------|
EOF

# ─── Summary ───────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Workspace criado com sucesso!${NC}"
echo -e "${GREEN}  Projeto: ${YELLOW}$PROJECT_NAME${NC}"
echo -e "${GREEN}  Diretório: ${YELLOW}$PROJECT_DIR${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}Estrutura criada:${NC}"
echo "    context/         — Declaração do problema, 5W1H, restrições"
echo "    domains/         — Relevance check e matriz M³"
echo "    team/            — Agentes especialistas + coordenador"
echo "    shared/          — Dados compartilhados entre agentes"
echo "    meetings/        — Atas, decisões e deadlocks"
echo "    publications/    — Artigos científicos"
echo "    vvv/             — Relatórios de validação e certificação"
echo ""
echo -e "  ${YELLOW}Próximos passos:${NC}"
echo "    1. Edite context/problem_statement.md com o problema"
echo "    2. Edite domains/relevance_check.md para mapear domínios"
echo "    3. Inicialize o coordenador: cd $PROJECT_DIR && bash team/coordinator/coordinator.sh init ."
echo "    4. Derive o time: bash team/coordinator/coordinator.sh derive-team"
echo "    5. Aloque tarefas: bash team/coordinator/coordinator.sh allocate \"<desc>\" <agente>"
echo ""
