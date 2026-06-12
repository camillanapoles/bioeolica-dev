#!/usr/bin/env bash
set -e
echo "Indexando com GitNexus (AST + Grafo de Dependências)..."
bunx gitnexus analyze . --force 2>/dev/null || echo "GitNexus não instalado ou erro"
bunx gitnexus mcp 2>/dev/null &
echo "MCP server GitNexus ativo"
