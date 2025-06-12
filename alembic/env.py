from logging.config import fileConfig
import asyncio

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection

from models import Base  


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
   
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        
        await connection.run_sync(do_run_migrations)

    
    await connectable.dispose()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        # здесь важно обернуть асинхронную функцию в asyncio.run
        asyncio.run(run_migrations_online())


if __name__ == "__main__":
    main()