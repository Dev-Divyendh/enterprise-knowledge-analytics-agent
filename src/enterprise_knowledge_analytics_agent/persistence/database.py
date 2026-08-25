from sqlalchemy import Engine, create_engine, text

from enterprise_knowledge_analytics_agent.config import Settings, get_settings


def create_database_engine(settings: Settings | None = None) -> Engine:
    """Create a SQLAlchemy engine without immediately opening a connection."""

    resolved_settings = settings or get_settings()

    if resolved_settings.database_url is None:
        raise RuntimeError("EKA_DATABASE_URL is required for database operations")

    return create_engine(
        resolved_settings.database_url,
        echo=resolved_settings.database_echo,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def check_database_health(engine: Engine) -> str:
    """Open a connection and return the current PostgreSQL database name."""

    with engine.connect() as connection:
        database_name = connection.execute(text("SELECT current_database()")).scalar_one()

    return str(database_name)
