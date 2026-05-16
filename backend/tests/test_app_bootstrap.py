from app.infrastructure.database.mysql import MySqlUnitOfWork
from app.infrastructure.vector.qdrant import QdrantVectorStore
from app.main import create_app


def test_app_bootstrap_registers_core_routes() -> None:
    app = create_app()

    routes = {route.path for route in app.routes}

    assert "/health" in routes
    assert "/ask" in routes
    assert "/telegram/webhook" in routes
    assert "/feedback" in routes
    assert "/attendances" in routes
    assert "/attendances/{attendance_id}" in routes
    assert "/documents" in routes
    assert "/documents/reindex" in routes
    assert "/metrics" in routes


def test_app_bootstrap_registers_integration_placeholders() -> None:
    app = create_app()

    assert isinstance(app.state.mysql_uow, MySqlUnitOfWork)
    assert app.state.mysql_uow.config.url
    assert isinstance(app.state.vector_store, QdrantVectorStore)
    assert app.state.vector_store.config.url
    assert app.state.vector_store.config.collection
