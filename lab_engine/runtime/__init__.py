"""Runtime event-driven do LAB-ENGINE (FASE 2, T05+).

Command bus + event store + handlers. O event store é uma **projeção sobre o
WAL** (``wal_logs``) — eventos de domínio são ``WalLog``s (decisão D-T05.1),
fiel ao princípio "source of truth único = WAL em BD" (arquitetura §2) e ao
mapeamento híbrido de D-T03.1. Uma tabela ``domain_events`` separada
duplicaria o source of truth e criaria drift — o WAL **já é** o log de eventos.
"""
