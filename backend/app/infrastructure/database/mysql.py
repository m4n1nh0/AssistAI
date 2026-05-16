from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.models import Base, create_engine


@dataclass(frozen=True, slots=True)
class MySqlConfig:
    url: str


class MySqlUnitOfWork:
    def __init__(self, config: MySqlConfig) -> None:
        self.config = config
        self.engine = create_engine(config.url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self._session_maker: sessionmaker[Session] = sessionmaker(
            bind=self.engine
        )

    @property
    def session_maker(self) -> sessionmaker[Session]:
        return self._session_maker

    def __enter__(self) -> MySqlUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.engine.dispose()

