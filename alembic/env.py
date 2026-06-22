"""Configuração do Alembic para a LAB-ENGINE (D-T03.3 — DB-agnóstico).

Engine e URL vêm das **settings** (``lab_engine.settings.get_settings``), NÃO
do ``alembic.ini`` — assim a configuração é zero-hardcoded (12-factor) e o
mesmo código de migration roda em SQLite (dev/test) e Postgres (prod).
``target_metadata = Base.metadata`` (+ import de ``lab_engine.wal.store`` para
registrar ``WalLogRow``) habilita o autogenerate.

``render_as_batch=True``: SQLite não suporta a maioria dos ``ALTER TABLE``; o
batch mode materializa o alter via tabela temporária — essencial para
migrations futuras (e no-op em Postgres).
"""
from logging.config import fileConfig

# Importa o módulo de store para registrar ``WalLogRow`` no ``Base.metadata``
# (necessário para autogenerate enxergar a tabela ``wal_logs``). noqa: o
# import é pelo efeito colateral de registro no metadata.
import lab_engine.wal.store  # noqa: F401
from alembic import context
from lab_engine.db import Base, make_engine
from lab_engine.settings import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData canônico da LAB-ENGINE — todas as tabelas ORM (WalLogRow etc.).
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # URL das settings (env/``.env``), não do ``alembic.ini`` (zero-hardcoded).
    url = get_settings().wal_db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Engine das settings — aplica PRAGMAS SQLite-condicional (D-T03.3) e
    # resolve a URL de ``LAB_ENGINE_WAL_DB_URL`` (env/``.env``).
    connectable = make_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
