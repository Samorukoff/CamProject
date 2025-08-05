import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from project.core.base.models import Base
from project.core.config.database.config import database_settings

# Импорт моделей для автогенерации
from project.auth.models import User
from project.company.models import Company
from project.subscribe.models import Subscription, SubscriptionType
from project.analysis.models import Point, AnalysisData

config = context.config
fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", database_settings.get_db_url())

target_metadata = Base.metadata


def run_migrations_offline():
    """Offline миграции"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Синхронная часть — конфигурация и запуск миграций"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Online миграции"""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=None,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run()

print("Loaded tables:")
for t in target_metadata.tables:
    print(" -", t)
