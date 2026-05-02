from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MySqlConfig:
    url: str


class MySqlUnitOfWork:
    def __init__(self, config: MySqlConfig) -> None:
        self.config = config

    def __enter__(self) -> "MySqlUnitOfWork":
        raise NotImplementedError("MySQL persistence will replace the in-memory adapter.")

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

