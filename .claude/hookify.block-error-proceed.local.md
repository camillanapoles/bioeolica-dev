---
name: block-error-proceed
enabled: true
event: prompt
pattern: task\s*(completed|done|finalizado|completo|proximo|próximo|continue|continuar|avanc|avançar|seguinte)
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: (?i)(task\s*(completed|done|finalizado|completo|proximo|próximo|continue|continuar|avanc|avançar|seguinte|next))
---

## 🚫 BLOQUEADO: Não pode avançar sem verificar erro anterior

**Regra violada:** Mandato $1 — NUNCA continuar tasks se erro ou incompleta.

### Antes de declarar qualquer task como completa:

1. **Verifique** se o último comando executado retornou exit code 0
2. **Se erro** (exit code != 0): PARE. Diagnostique com GitNexus antes de qualquer ação corretiva:
   ```
   node .gitnexus/run.cjs context <symbol> --file <arquivo>
   ```
3. **Corrija** o erro específico
4. **Verifique** a correção (exit code 0)
5. **Confirme** com o usuário: "Erro corrigido. Prosseguir?"

### O que NÃO fazer:
- ❌ Pular para próxima task sem corrigir erro anterior
- ❌ Ignorar exit code diferente de 0
- ❌ Assumir que arquivo existe = task completa
- ❌ Mover para T(N+1) sem T(N) verificada com sucesso

**Lembre-se:** Se T012 falhou com exit code 1, você NÃO pode ir para T013 até T012 estar 100% corrigida e verificada.
