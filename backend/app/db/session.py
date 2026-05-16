from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.mysql_url,
    future=True,
    pool_pre_ping=True,
    connect_args={"charset": "utf8mb4"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db() -> None:
    from app.db.models import Base as ModelsBase

    try:
        ModelsBase.metadata.create_all(bind=engine)
    except Exception:
        # Falha de inicialização de banco não deve impedir o backend de rodar na POC.
        pass
