from __future__ import annotations
from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure project root is on sys.path so "app" imports work when running alembic
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import Base first
from app.db.base import Base  # noqa: E402

# Import all models to ensure they're registered with Base.metadata
from app.models.user import User  # noqa: F401,E402
from app.models.post import Post, Reaction  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Resolve database URL from environment or default
database_url = os.getenv("DATABASE_URL") or "postgresql://neondb_owner:npg_l4VsBq8gnHJM@ep-green-hat-adw2lsbg-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

section = config.get_section(config.config_ini_section)
if section is not None:
    section["sqlalchemy.url"] = database_url
# Also set on the main option to cover all code paths
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, 
        target_metadata=target_metadata, 
        literal_binds=True, 
        dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {}, 
        prefix="sqlalchemy.", 
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()