#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
MAX_ATTEMPTS=3

# [PATCH CIRÚRGICO 3] Auto-detecta diretório do script para caminhos absolutos
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
FSM_SCRIPT="$SCRIPT_DIR/python/fsm_orchestrator.py"

log() { echo -e "\033[0;34m[SELF-HEALING]\033[0m $1"; }

check_dod() {
    local exit_code=0

    if [[ -f "package.json" ]]; then bun run build 2>&1 | tail -10 || exit_code=1; fi
    if [[ -f "pyproject.toml" ]]; then uv run python -m pyright . 2>&1 | tail -10 || exit_code=1; fi

    if [[ -f "package.json" ]]; then bun test 2>&1 | tail -20 || exit_code=1; fi
    if [[ -f "pyproject.toml" ]]; then uv run pytest --tb=line -q || exit_code=1; fi

    local diff_lines
    diff_lines=$(git diff --shortstat 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
    if [[ $diff_lines -gt 120 ]]; then
        log "Diff muito grande ($diff_lines linhas)"
        exit_code=1
    fi

    return $exit_code
}

attempt=1
while [[ $attempt -le $MAX_ATTEMPTS ]]; do
    log "Tentativa $attempt/$MAX_ATTEMPTS para $TASK_ID"

    if check_dod; then
        git add -A
        git commit -m "feat: $TASK_ID (self-healed • attempt $attempt)" || true
        python3 "$FSM_SCRIPT" status
        log "✅ Tarefa concluída e validada"
        exit 0
    else
        log "Falha na Definition of Done. Auto-correção em andamento..."
        ((attempt++))
    fi
done

log "❌ Falha após $MAX_ATTEMPTS tentativas"
exit 1
