#!/usr/bin/env python3
"""
Agentic FSM Orchestrator v2.6 — EXTREME DETERMINISTIC
Motor determinístico de estados com validação Pydantic
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class DefinitionOfDone(BaseModel):
    exit_code_zero: bool = True
    tests_pass: bool = True
    diff_cirurgical: bool = True
    no_new_warnings: bool = True

class AgenticState(BaseModel):
    version: str = "2.6"
    current_phase: Literal["INIT", "SPECIFY", "MAD", "TASKS", "EXECUTE", "DONE", "ERROR"] = "INIT"
    current_task_id: Optional[str] = None
    fsm_state: Literal["IDLE", "AWAITING_HUMAN_SPEC", "AWAITING_HUMAN_PLAN", "EXECUTING", "SELF_HEALING"] = "IDLE"
    human_approved_spec: bool = False
    human_approved_plan: bool = False
    tasks_completed: int = 0
    total_tasks: int = 0
    self_healing_attempts: int = 0
    max_healing_attempts: int = 3
    last_validation: Optional[str] = None
    definition_of_done: DefinitionOfDone = Field(default_factory=DefinitionOfDone)

    @field_validator("fsm_state")
    @classmethod
    def validate_transitions(cls, v, info):
        data = info.data
        if v == "EXECUTING" and not data.get("human_approved_plan"):
            raise ValueError("Cannot enter EXECUTING without human_approved_plan=True")
        if v == "SELF_HEALING" and data.get("self_healing_attempts", 0) > data.get("max_healing_attempts", 3):
            raise ValueError("Max self-healing attempts exceeded")
        return v

class PayloadValidator(BaseModel):
    action: Literal["specify", "plan", "execute_task", "self_heal"]
    task_id: Optional[str] = None
    content: str = Field(min_length=10)
    approved_by_human: bool = False

    @field_validator("approved_by_human")
    @classmethod
    def must_be_approved(cls, v, info):
        if info.data.get("action") in ["execute_task", "self_heal"] and not v:
            raise ValueError("Human approval required for execution actions")
        return v

class AgenticFSM:
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> AgenticState:
        if self.state_file.exists():
            data = json.loads(self.state_file.read_text())
            return AgenticState(**data)
        return AgenticState()

    def _save_state(self):
        self.state_file.write_text(json.dumps(self.state.model_dump(), indent=2, default=str))

    def transition(self, new_phase: str, **kwargs) -> bool:
        old_phase = self.state.current_phase
        old_fsm = self.state.fsm_state

        if new_phase == "MAD" and not self.state.human_approved_spec:
            print("❌ BLOQUEADO: Especifique e aprove primeiro (human_approved_spec)")
            return False
        if new_phase == "EXECUTE" and not self.state.human_approved_plan:
            print("❌ BLOQUEADO: Plano de arquitetura deve ser aprovado")
            return False
        if new_phase == "SELF_HEALING" and self.state.self_healing_attempts >= self.state.max_healing_attempts:
            print("❌ BLOQUEADO: Máximo de tentativas de self-healing atingido")
            return False

        self.state.current_phase = new_phase  # type: ignore
        for k, v in kwargs.items():
            if hasattr(self.state, k):
                setattr(self.state, k, v)

        self.state.last_validation = datetime.now().isoformat()
        self._save_state()
        print(f"✅ Transição: {old_phase} → {new_phase} | FSM: {old_fsm} → {self.state.fsm_state}")
        return True

    def validate_payload(self, payload: dict) -> bool:
        try:
            PayloadValidator(**payload)
            return True
        except Exception as e:
            print(f"❌ Payload inválido (Type Safety): {e}")
            return False

    def request_human_gate(self, gate: str) -> bool:
        print(f"\n{'='*60}")
        print(f"🚨 HUMAN GATE: {gate}")
        print(f"{'='*60}")
        answer = input("Aprovar? (Y/N): ").strip().upper()
        approved = answer == "Y"

        if gate == "SPEC":
            self.state.human_approved_spec = approved
        elif gate == "PLAN":
            self.state.human_approved_plan = approved

        self._save_state()
        return approved

    def get_status(self):
        print(json.dumps(self.state.model_dump(), indent=2, default=str))

if __name__ == "__main__":
    fsm = AgenticFSM(Path(".agent/state.json"))

    if len(sys.argv) < 2:
        print("Uso: python fsm_orchestrator.py {specify|plan|execute|status|gate}")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "specify":
        if fsm.transition("SPECIFY"):
            fsm.request_human_gate("SPEC")
    elif cmd == "plan":
        if fsm.transition("MAD"):
            fsm.request_human_gate("PLAN")
    elif cmd == "execute":
        if fsm.transition("EXECUTE"):
            print("Pronto para execução incremental com self-healing")
    elif cmd == "status":
        fsm.get_status()
    elif cmd == "gate":
        gate = sys.argv[2] if len(sys.argv) > 2 else "SPEC"
        fsm.request_human_gate(gate)
    else:
        print("Comando desconhecido")
