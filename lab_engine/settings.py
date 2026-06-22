"""Configuração da LAB-ENGINE — zero-hardcoded (12-factor).

Toda configuração sensível a ambiente (DB URL, timeouts, etc.) vive aqui e é
carregada de variáveis de ambiente (prefixo ``LAB_ENGINE_``) ou de um ``.env``.
Nenhum script/setor do runtime define ``export VAR=...`` — isso quebraria a
reprodutibilidade (mandato "PROIBIDO setar variáveis nos scripts"). Defaults
existem só como fallback idiomático, **sempre** sobrescrevíveis via env.

Uso::

    from lab_engine.settings import get_settings
    db_url = get_settings().wal_db_url   # lê LAB_ENGINE_WAL_DB_URL ou default
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração global da LAB-ENGINE (env-driven, imutável após carga).

    Variáveis de ambiente (prefixo ``LAB_ENGINE_``):
        - ``LAB_ENGINE_WAL_DB_URL``: URL do banco do WAL (default SQLite local).
          ``sqlite:///data/lab_engine.db`` (dev) · ``postgresql+psycopg://user@host/db``
          (prod) · ``sqlite://`` (testes in-memory).
    """

    model_config = SettingsConfigDict(
        env_prefix="LAB_ENGINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # Source-of-truth do WAL — BD relacional durável (D-T03.3, D-T03.4).
    # SQLite (dev/test) ou Postgres (prod); nunca Redis como source-of-truth.
    wal_db_url: str = "sqlite:///data/lab_engine.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton de Settings (cacheado). Use ``get_settings.cache_clear()`` em testes."""
    return Settings()


__all__ = ["Settings", "get_settings"]
