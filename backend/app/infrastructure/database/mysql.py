from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.infrastructure.database.session import SessionLocal


@dataclass(frozen=True, slots=True)
class MySqlConfig:
    url: str


class MySqlUnitOfWork:
    def __init__(self, config: MySqlConfig) -> None:
        self.config = config
        self.session: Session | None = None

    def __enter__(self) -> "MySqlUnitOfWork":
        self.session = SessionLocal()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.session:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()

