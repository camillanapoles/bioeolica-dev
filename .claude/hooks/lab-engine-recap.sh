#!/usr/bin/env bash
# Recap canônico LAB-ENGINE — injetado em TODO UserPromptSubmit.
# Defesa primária anti-fuga-de-escopo: garante que o contexto do plano ativo
# (fontes canônicas + mandatos M0-M4 + garantismo + escopos válidos vs fuga)
# está SEMPRE presente no contexto do modelo. Defesa de persistência ao plano.
#
# Output: JSON com hookSpecificOutput.additionalContext (UserPromptSubmit).
set -euo pipefail

# Resolve o diretório do projeto (CLAUDE_PROJECT_DIR é setado pelo Claude Code;
# fallback para o CWD p/ teste manual via pipe).
project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
recap_file="${project_dir}/.claude/hooks/recap.md"

# Lê o texto do recap (editável em recap.md, sem tocar neste script).
recap_text="$(cat "$recap_file" 2>/dev/null || echo "AVISO: recap.md ausente em ${recap_file}")"

# Gera JSON válido — jq escapa o texto (acentos, aspas, newlines) corretamente.
jq -nc --arg ctx "$recap_text" '{
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: $ctx
  }
}'
