#!/usr/bin/env python3
"""Validador de payloads gerados pelo modelo"""
import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from fsm_orchestrator import PayloadValidator

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python payload_validator.py '<json_payload>'")
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
        PayloadValidator(**payload)
        print("✅ Payload validado com sucesso (Type Safety)")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Payload inválido: {e}")
        sys.exit(1)
