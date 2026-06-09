#!/usr/bin/env bash
# coordinator.sh
# Agente Coordenador — orquestração multi-agente derivada do contexto
# Uso: ./coordinator.sh <comando> [args...]
#
# Comandos:
#   init     <project-dir>   Inicializa projeto: lê contexto, deriva time, aloca
#   status                   Status do time e alocações atuais
#   allocate [agent-id]      Aloca tarefas (para agente específico ou todos)
#   meeting  [agent-id...]   Convoca reunião entre agentes especificados
#   deadlock                 Detecta e tenta resolver deadlocks
#   report                   Gera relatório de status do projeto
#   agenda                   Mostra reuniões agendadas

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT_DIR="$PROJECT_ROOT/context"
ALLOCATION_FILE="$SCRIPT_DIR/allocation.md"
AGENDA_FILE="$SCRIPT_DIR/agenda.md"
DEADLOCK_FILE="$PROJECT_ROOT/meetings/deadlocks.md"
DECISION_LOG="$PROJECT_ROOT/meetings/decision_log.md"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

mkdir -p "$SCRIPT_DIR/atas" "$(dirname "$DEADLOCK_FILE")" "$(dirname "$DECISION_LOG")"

# ─── Help ──────────────────────────────────────────────────────────────────

if [ $# -lt 1 ]; then
    echo -e "${CYAN}Agente Coordenador — Orquestração Multi-Agente${NC}"
    echo ""
    echo "Comandos:"
    echo "  init     <project-dir>   Inicializa projeto: lê contexto, deriva time"
    echo "  status                   Status do time e alocações"
    echo "  allocate [agent-id]      Aloca tarefas para agente(s)"
    echo "  meeting  [agent-id...]   Convoca reunião entre agentes"
    echo "  deadlock                 Detecta e resolve deadlocks"
    echo "  report                   Relatório de status do projeto"
    echo "  agenda                   Mostra reuniões agendadas"
    exit 0
fi

COMMAND="$1"
shift

# ─── Funções ───────────────────────────────────────────────────────────────

log_event() {
    local event="$1"
    local details="${2:-}"
    echo "[$(date -Iseconds)] COORD | $event | $details" >> "$SCRIPT_DIR/../.coordinator.log"
}

check_domain_relevance() {
    local domain="$1"
    local context_dir="$2"
    local relevance_file="$context_dir/domains/relevance_check.md"

    if [ ! -f "$relevance_file" ]; then
        echo "PENDING"
        return
    fi

    if grep -qi "$domain.*SIM\|$domain.*sim\|$domain.*yes\|$domain.*YES" "$relevance_file" 2>/dev/null; then
        echo "SIM"
    elif grep -qi "$domain.*NAO\|$domain.*nao\|$domain.*NÃO\|$domain.*no\|$domain.*NO\|$domain.*N" "$relevance_file" 2>/dev/null; then
        echo "NAO"
    else
        echo "PENDING"
    fi
}

get_agent_id() {
    local domain="$1"
    # Normaliza nome do domínio para ID de agente
    echo "agent-$(echo "$domain" | iconv -f utf-8 -t ascii//TRANSLIT 2>/dev/null || echo "$domain" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9_-')"
}

get_agent_domain() {
    local agent_dir="$1"
    # Extrai domínio do nome do diretório agent-<dominio>
    echo "$agent_dir" | sed 's/^agent-//' | tr '-' ' '
}

# ─── init ──────────────────────────────────────────────────────────────────

if [ "$COMMAND" = "init" ]; then
    PROJECT_DIR="${1:-}"
    if [ -z "$PROJECT_DIR" ]; then
        PROJECT_DIR="$PROJECT_ROOT"
    fi

    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  COORDENADOR: Inicializando projeto${NC}"
    echo -e "${CYAN}  Diretório: $PROJECT_DIR${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"

    # Lê contexto F1 — problem_statement
    PROBLEM_FILE="$PROJECT_DIR/context/problem_statement.md"
    DOMAINS_FILE="$PROJECT_DIR/context/domains/relevance_check.md"

    if [ -f "$PROBLEM_FILE" ]; then
        echo -e "\n${YELLOW}[F1] Contexto do Problema:${NC}"
        head -20 "$PROBLEM_FILE"
    else
        echo -e "\n${YELLOW}[F1] Nenhum problem_statement.md encontrado.${NC}"
        echo -e "  Crie em: $PROBLEM_FILE"
    fi

    # ─── F2: Mapear Domínios — Deriva time do contexto ──────────────────

    echo -e "\n${YELLOW}[F2] Mapeando Domínios — Derivando Time do Contexto...${NC}"
    echo ""

    # Lista de 10 domínios base (expansível — o processo é o invariante)
    DOMAINS=(
        "mecanica:Engenharia Mecânica"
        "fluidos:Mecânica dos Fluidos"
        "termo:Termodinâmica"
        "energia:Sistemas Energéticos"
        "eletricidade:Engenharia Eletrotécnica"
        "materiais:Engenharia de Materiais"
        "construcao:Métodos de Construção"
        "ambiente:Engenharia Ambiental"
        "normativo:Engenharia Normativa"
        "economico:Engenharia Econômica"
    )

    # Cria diretório de domínios
    mkdir -p "$PROJECT_DIR/context/domains"

    DECLARED_AGENTS=()
    PENDING_DOMAINS=()

    for domain_entry in "${DOMAINS[@]}"; do
        DOMAIN_ID="${domain_entry%%:*}"
        DOMAIN_NAME="${domain_entry##*:}"
        AGENT_ID="agent-$DOMAIN_ID"

        # Verifica relevance_check.md para este domínio
        RELEVANCE="PENDING"
        if [ -f "$DOMAINS_FILE" ]; then
            if grep -qi "^$DOMAIN_ID" "$DOMAINS_FILE" 2>/dev/null; then
                RELEVANCE=$(grep -i "^$DOMAIN_ID" "$DOMAINS_FILE" | head -1 | grep -oE 'SIM|NAO|PENDING|DUVIDA' || echo "PENDING")
            fi
        fi

        # Se não há relevance_check.md, verifica se diretório do agente existe
        AGENT_DIR="$PROJECT_DIR/team/$AGENT_ID"
        if [ ! -f "$DOMAINS_FILE" ] && [ -d "$AGENT_DIR" ]; then
            RELEVANCE="SIM"
        fi

        case "$RELEVANCE" in
            SIM)
                echo -e "  ${GREEN}✓${NC} $DOMAIN_ID ($DOMAIN_NAME) — ${GREEN}RELEVANTE${NC}"
                DECLARED_AGENTS+=("$AGENT_ID:$DOMAIN_NAME")
                # Garante que diretório do agente existe
                mkdir -p "$AGENT_DIR"
                ;;
            DUVIDA)
                echo -e "  ${YELLOW}?${NC} $DOMAIN_ID ($DOMAIN_NAME) — ${YELLOW}INVESTIGAR${NC}"
                PENDING_DOMAINS+=("$DOMAIN_ID:$DOMAIN_NAME")
                ;;
            NAO)
                echo -e "  ${RED}✗${NC} $DOMAIN_ID ($DOMAIN_NAME) — ${RED}NÃO RELEVANTE${NC}"
                ;;
            PENDING)
                echo -e "  ${YELLOW}?${NC} $DOMAIN_ID ($DOMAIN_NAME) — ${YELLOW}PENDENTE (sem avaliação)${NC}"
                PENDING_DOMAINS+=("$DOMAIN_ID:$DOMAIN_NAME")
                ;;
        esac
    done

    # ─── Composição do Time ────────────────────────────────────────────

    echo ""
    echo -e "${CYAN}────────────────────────────────────────────────────────${NC}"
    echo -e "${CYAN}  COMPOSIÇÃO DO TIME${NC}"
    echo -e "${CYAN}────────────────────────────────────────────────────────${NC}"
    echo ""

    if [ ${#DECLARED_AGENTS[@]} -eq 0 ]; then
        echo -e "  ${YELLOW}Nenhum agente confirmado. Crie context/domains/relevance_check.md${NC}"
        echo -e "  para avaliar a relevância de cada domínio.${NC}"
    else
        echo -e "  ${GREEN}Agentes Convocados (${#DECLARED_AGENTS[@]}):${NC}"
        for agent_entry in "${DECLARED_AGENTS[@]}"; do
            AGENT_ID="${agent_entry%%:*}"
            DOMAIN_NAME="${agent_entry##*:}"
            echo -e "    ${GREEN}→${NC} $AGENT_ID — $DOMAIN_NAME"
        done

        # Cria diretório do coordenador no team
        mkdir -p "$PROJECT_DIR/team/coordinator/atas"

        # Gera allocation.md
        echo "# Alocação de Tarefas — $(basename "$PROJECT_DIR")" > "$ALLOCATION_FILE"
        echo "" >> "$ALLOCATION_FILE"
        echo "Gerado em: $(date -Iseconds) pelo Agente Coordenador" >> "$ALLOCATION_FILE"
        echo "" >> "$ALLOCATION_FILE"
        echo "## Agentes Convocados" >> "$ALLOCATION_FILE"
        echo "" >> "$ALLOCATION_FILE"
        echo "| Domínio | Agente | Status | Tarefas |" >> "$ALLOCATION_FILE"
        echo "|---------|--------|--------|---------|" >> "$ALLOCATION_FILE"
        for agent_entry in "${DECLARED_AGENTS[@]}"; do
            AGENT_ID="${agent_entry%%:*}"
            DOMAIN_NAME="${agent_entry##*:}"
            echo "| $DOMAIN_NAME | \`$AGENT_ID\` | 🟢 Alocado | Pendente |" >> "$ALLOCATION_FILE"
        done

        echo "" >> "$ALLOCATION_FILE"
        echo "## Agentes Pendentes de Investigação" >> "$ALLOCATION_FILE"
        echo "" >> "$ALLOCATION_FILE"
        for pending in "${PENDING_DOMAINS[@]}"; do
            DOMAIN_ID="${pending%%:*}"
            DOMAIN_NAME="${pending##*:}"
            echo "- **$DOMAIN_NAME** (\`$DOMAIN_ID\`) — aguardando relevance_check" >> "$ALLOCATION_FILE"
        done

        echo -e "\n  ${GREEN}✓ allocation.md gerado${NC}"
    fi

    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  INICIALIZAÇÃO COMPLETA${NC}"
    if [ ${#PENDING_DOMAINS[@]} -gt 0 ]; then
        echo -e "${YELLOW}  ${#PENDING_DOMAINS[@]} domínio(s) pendente(s) de avaliação${NC}"
    fi
    echo -e "${GREEN}  ${#DECLARED_AGENTS[@]} agente(s) confirmado(s)${NC}"
    echo -e "${GREEN}  Próximo passo: ./coordinator.sh allocate${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"

    log_event "INIT" "project=$(basename "$PROJECT_DIR") agents=${#DECLARED_AGENTS[@]} pending=${#PENDING_DOMAINS[@]}"
    exit 0
fi

# ─── allocate ──────────────────────────────────────────────────────────────

if [ "$COMMAND" = "allocate" ]; then
    TARGET_AGENT="${1:-all}"

    echo -e "${CYAN}Alocação de Tarefas${NC}"
    echo ""

    # Lê a composição do time do allocation.md
    if [ ! -f "$ALLOCATION_FILE" ]; then
        echo -e "${RED}ERRO: Nenhuma alocação encontrada. Execute 'init' primeiro.${NC}"
        exit 1
    fi

    # Extrai agentes do allocation.md
    AGENTS=$(grep '| `agent-' "$ALLOCATION_FILE" | sed 's/.*| `//;s/`.*//')

    if [ -z "$AGENTS" ]; then
        echo -e "${YELLOW}Nenhum agente alocado. Execute 'init' primeiro.${NC}"
        exit 0
    fi

    for AGENT in $AGENTS; do
        if [ "$TARGET_AGENT" != "all" ] && [ "$AGENT" != "$TARGET_AGENT" ]; then
            continue
        fi

        DOMAIN=$(get_agent_domain "$AGENT")
        echo -e "${YELLOW}Alocando tarefas para: $AGENT ($DOMAIN)${NC}"

        # Cria diretório do agente
        AGENT_DIR="$PROJECT_DIR/team/$AGENT"
        mkdir -p "$AGENT_DIR"

        # Gera tarefas padrão por domínio
        TASKS_FILE="$AGENT_DIR/tasks.md"
        cat > "$TASKS_FILE" << TASKSEOF
# Tarefas — $AGENT
# Domínio: $DOMAIN
# Alocado por: Coordenador em $(date -Iseconds)

## Pendentes
- [ ] Analisar contexto do problema (F1)
- [ ] Aplicar M³ ao domínio (F3)
- [ ] Selecionar métodos e ferramentas (F4)
- [ ] Executar simulações (F5)
- [ ] Documentar resultados (F6)
- [ ] Publicar contexto em shared/ (após quality gates)

## Em Andamento
*(nenhuma)*

## Concluídas
*(nenhuma)*

## Dependências
- Este agente depende de: \`(mapear durante execução)\`
- Dependentes deste agente: \`(mapear durante execução)\`
TASKSEOF
        echo -e "  ${GREEN}✓ Tarefas geradas: $TASKS_FILE${NC}"
    done

    echo ""
    echo -e "${GREEN}Alocação concluída.${NC}"

    # Atualiza allocation.md
    if [ "$TARGET_AGENT" = "all" ]; then
        sed -i 's/| Pendente |/| Alocada |/g' "$ALLOCATION_FILE"
        log_event "ALLOCATE_ALL" "all agents allocated"
    else
        log_event "ALLOCATE" "agent=$TARGET_AGENT"
    fi
    exit 0
fi

# ─── meeting ───────────────────────────────────────────────────────────────

if [ "$COMMAND" = "meeting" ]; then
    if [ $# -lt 1 ]; then
        echo -e "${RED}ERRO: Informe ao menos um agente para a reunião.${NC}"
        echo -e "Uso: ./coordinator.sh meeting <agent-id> [agent-id...]"
        exit 1
    fi

    MEETING_ID="REUNIAO-$(date +%Y%m%d)-$(openssl rand -hex 3 2>/dev/null || echo "$(date +%s)")"
    MEETING_DATE=$(date -Iseconds)
    PARTICIPANTS="$*"
    ATA_FILE="$SCRIPT_DIR/atas/${MEETING_ID}.md"

    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  CONVOCAÇÃO DE REUNIÃO: $MEETING_ID${NC}"
    echo -e "${CYAN}  Participantes: $PARTICIPANTS${NC}"
    echo -e "${CYAN}  Data: $MEETING_DATE${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"

    # Cria ata
    cat > "$ATA_FILE" << ATAEOF
# Ata de Reunião — $MEETING_ID

**Data:** $MEETING_DATE
**Participantes:** $PARTICIPANTS
**Convocado por:** Coordenador

## Pauta

- Alinhamento de interconexões entre domínios
- Revisão de dependências
- Resolução de conflitos de contexto

## Discussão

*(a ser preenchido durante a reunião)*

## Decisões

| Decisão | Responsável | Data |
|---------|-------------|------|
| - | - | - |

## Action Items

| Ação | Responsável | Prazo |
|------|-------------|-------|
| - | - | - |

---
Ata gerada automaticamente pelo Agente Coordenador
ATAEOF

    echo -e "${GREEN}✓ Ata criada: $ATA_FILE${NC}"

    # Registra na agenda
    {
        echo ""
        echo "## $MEETING_ID"
        echo "**Data:** $MEETING_DATE"
        echo "**Participantes:** $PARTICIPANTS"
        echo "**Status:** agendada"
        echo "**Ata:** $ATA_FILE"
        echo ""
    } >> "$AGENDA_FILE"

    log_event "MEETING" "id=$MEETING_ID participants=$PARTICIPANTS"
    exit 0
fi

# ─── deadlock ──────────────────────────────────────────────────────────────

if [ "$COMMAND" = "deadlock" ]; then
    echo -e "${CYAN}Detectando Deadlocks...${NC}"
    echo ""

    # Procura por contextos DISPUTED
    DISPUTED=()
    while IFS= read -r -d '' json_file; do
        CONTEXT_ID=$(jq -r '.id // "unknown"' "$json_file" 2>/dev/null)
        STATUS=$(jq -r '.lineage.validation_status // empty' "$json_file" 2>/dev/null)

        if [ "$STATUS" = "DISPUTED" ]; then
            CREATED_BY=$(jq -r '.lineage.created_by // "unknown"' "$json_file" 2>/dev/null)
            DISPUTED+=("$CONTEXT_ID ($CREATED_BY)")
            echo -e "  ${RED}✗ CONFLITO:${NC} $CONTEXT_ID (criado por: $CREATED_BY)"
        fi
    done < <(find "$CONTEXT_DIR" -name "*.json" -not -name "index.json" -not -name "graph.json" -not -name "ontology.json" -not -name "quality_gates.json" -print0 2>/dev/null)

    if [ ${#DISPUTED[@]} -eq 0 ]; then
        echo -e "  ${GREEN}✓ Nenhum deadlock detectado.${NC}"
    else
        echo ""
        echo -e "${YELLOW}Deadlocks detectados: ${#DISPUTED[@]}${NC}"
        echo ""

        # Registra no deadlock log
        {
            echo "## Deadlock $(date -Iseconds)"
            echo "Contextos em conflito:"
            for d in "${DISPUTED[@]}"; do
                echo "  - $d"
            done
            echo "Status: PENDENTE_RESOLUCAO"
            echo "Resolução: (pendente — convocar reunião entre agentes envolvidos)"
            echo ""
        } >> "$DEADLOCK_FILE"

        echo -e "${YELLOW}Registrado em: $DEADLOCK_FILE${NC}"
        echo -e "${YELLOW}Ação sugerida: ./coordinator.sh meeting ${DISPUTED[*]}${NC}"
    fi

    # Verifica dependências circulares entre agentes
    echo ""
    echo -e "${CYAN}Verificando dependências circulares entre agentes...${NC}"

    # Lê tasks.md de cada agente
    declare -A DEPS_MAP
    for agent_dir in "$PROJECT_DIR/team/agent-"*/; do
        [ -d "$agent_dir" ] || continue
        AGENT_ID=$(basename "$agent_dir")
        TASKS_FILE="$agent_dir/tasks.md"
        if [ -f "$TASKS_FILE" ]; then
            # Extrai dependências
            DEPS=$(grep -oP '(?<=Este agente depende de: `).*?(?=`)' "$TASKS_FILE" 2>/dev/null || true)
            if [ -n "$DEPS" ]; then
                DEPS_MAP["$AGENT_ID"]="$DEPS"
            fi
        fi
    done

    # Detecta ciclos (algoritmo simples de detecção de ciclo em grafo)
    CIRCULAR=false
    for agent in "${!DEPS_MAP[@]}"; do
        for dep in ${DEPS_MAP[$agent]}; do
            if [ -n "${DEPS_MAP[$dep]:-}" ]; then
                if echo "${DEPS_MAP[$dep]}" | grep -q "$agent"; then
                    echo -e "  ${RED}✗ CICLO DETECTADO:${NC} $agent ↔ $dep"
                    CIRCULAR=true
                fi
            fi
        done
    done

    if [ "$CIRCULAR" = false ]; then
        echo -e "  ${GREEN}✓ Nenhuma dependência circular detectada.${NC}"
    fi

    exit 0
fi

# ─── status ────────────────────────────────────────────────────────────────

if [ "$COMMAND" = "status" ]; then
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  STATUS DO PROJETO${NC}"
    echo -e "${CYAN}  $(basename "$PROJECT_ROOT")${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo ""

    # Agentes
    echo -e "${YELLOW}Agentes:${NC}"
    AGENT_COUNT=0
    for agent_dir in "$PROJECT_DIR/team/agent-"*/; do
        [ -d "$agent_dir" ] || continue
        AGENT_ID=$(basename "$agent_dir")
        TASKS_FILE="$agent_dir/tasks.md"
        if [ -f "$TASKS_FILE" ]; then
            PENDING=$(grep -c '\- \[ \]' "$TASKS_FILE" 2>/dev/null || echo 0)
            DONE=$(grep -c '\- \[x\]' "$TASKS_FILE" 2>/dev/null || echo 0)
            echo -e "  ${GREEN}→${NC} $AGENT_ID — ${YELLOW}$PENDING pendente(s)${NC}, ${GREEN}$DONE concluída(s)${NC}"
        else
            echo -e "  ${GREEN}→${NC} $AGENT_ID — ${YELLOW}sem tarefas alocadas${NC}"
        fi
        AGENT_COUNT=$((AGENT_COUNT + 1))
    done

    if [ $AGENT_COUNT -eq 0 ]; then
        echo -e "  ${YELLOW}Nenhum agente encontrado. Execute 'init' primeiro.${NC}"
    fi
    echo -e "  Total: $AGENT_COUNT agente(s)"
    echo ""

    # Contextos
    echo -e "${YELLOW}Contextos:${NC}"
    CONTEXT_COUNT=0
    for class_dir in "$CONTEXT_DIR"/*/; do
        [ -d "$class_dir" ] || continue
        CLASS=$(basename "$class_dir")
        COUNT=$(find "$class_dir" -maxdepth 1 -name "*.json" 2>/dev/null | wc -l)
        if [ "$COUNT" -gt 0 ]; then
            echo -e "  ${GREEN}→${NC} $CLASS: $COUNT contexto(s)"
        fi
        CONTEXT_COUNT=$((CONTEXT_COUNT + COUNT))
    done
    echo -e "  Total: $CONTEXT_COUNT contexto(s)"
    echo ""

    # Deadlocks
    echo -e "${YELLOW}Deadlocks:${NC}"
    if [ -f "$DEADLOCK_FILE" ]; then
        DEADLOCK_COUNT=$(grep -c '^## Deadlock' "$DEADLOCK_FILE" 2>/dev/null || echo 0)
        if [ "$DEADLOCK_COUNT" -gt 0 ]; then
            echo -e "  ${RED}$DEADLOCK_COUNT deadlock(s) registrado(s)${NC}"
        else
            echo -e "  ${GREEN}Nenhum deadlock registrado${NC}"
        fi
    else
        echo -e "  ${GREEN}Nenhum deadlock registrado${NC}"
    fi

    # Reuniões
    echo ""
    echo -e "${YELLOW}Reuniões:${NC}"
    ATA_COUNT=$(find "$SCRIPT_DIR/atas" -name "*.md" 2>/dev/null | wc -l)
    echo -e "  $ATA_COUNT ata(s) de reunião realizada(s)"
    if [ -f "$AGENDA_FILE" ]; then
        AGENDADAS=$(grep -c 'Status: agendada' "$AGENDA_FILE" 2>/dev/null || echo 0)
        echo -e "  $AGENDADAS reunião(ões) agendada(s)"
    fi

    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    exit 0
fi

# ─── report ────────────────────────────────────────────────────────────────

if [ "$COMMAND" = "report" ]; then
    REPORT_FILE="$PROJECT_DIR/meetings/coordinator_report_$(date +%Y%m%d).md"

    echo -e "${CYAN}Gerando relatório de status...${NC}"

    cat > "$REPORT_FILE" << REPORTEOF
# Relatório do Coordenador — $(date +%Y%m%d)

**Gerado em:** $(date -Iseconds)
**Projeto:** $(basename "$PROJECT_ROOT")

## Time

| Agente | Domínio | Tarefas Pendentes | Tarefas Concluídas |
|--------|---------|------------------|-------------------|
REPORTEOF

    for agent_dir in "$PROJECT_DIR/team/agent-"*/; do
        [ -d "$agent_dir" ] || continue
        AGENT_ID=$(basename "$agent_dir")
        DOMAIN=$(get_agent_domain "$AGENT_ID")
        TASKS_FILE="$agent_dir/tasks.md"
        if [ -f "$TASKS_FILE" ]; then
            PENDING=$(grep -c '\- \[ \]' "$TASKS_FILE" 2>/dev/null || echo 0)
            DONE=$(grep -c '\- \[x\]' "$TASKS_FILE" 2>/dev/null || echo 0)
        else
            PENDING=0
            DONE=0
        fi
        echo "| \`$AGENT_ID\` | $DOMAIN | $PENDING | $DONE |" >> "$REPORT_FILE"
    done

    echo -e "\n## Contextos Publicados\n" >> "$REPORT_FILE"
    find "$CONTEXT_DIR" -name "*.json" -not -name "index.json" -not -name "graph.json" -not -name "ontology.json" -not -name "quality_gates.json" -exec basename {} \; >> "$REPORT_FILE" 2>/dev/null

    echo -e "\n## Deadlocks\n" >> "$REPORT_FILE"
    if [ -f "$DEADLOCK_FILE" ]; then
        cat "$DEADLOCK_FILE" >> "$REPORT_FILE"
    else
        echo "Nenhum deadlock registrado." >> "$REPORT_FILE"
    fi

    echo -e "${GREEN}✓ Relatório gerado: $REPORT_FILE${NC}"
    log_event "REPORT" "report=$REPORT_FILE"
    exit 0
fi

# ─── agenda ────────────────────────────────────────────────────────────────

if [ "$COMMAND" = "agenda" ]; then
    if [ ! -f "$AGENDA_FILE" ]; then
        echo -e "${YELLOW}Nenhuma reunião agendada.${NC}"
        exit 0
    fi
    echo -e "${CYAN}Reuniões Agendadas:${NC}"
    echo ""
    awk '/^## REUNIAO/{flag=1} flag; /^Status: agendada/{flag=0}' "$AGENDA_FILE" 2>/dev/null || echo "  ${YELLOW}Nenhuma reunião agendada.${NC}"
    exit 0
fi

# ─── Comando desconhecido ──────────────────────────────────────────────────

echo -e "${RED}Comando desconhecido: $COMMAND${NC}"
echo "Comandos válidos: init, status, allocate, meeting, deadlock, report, agenda"
exit 1
