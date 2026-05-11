import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import Settings, get_settings
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import QdrantVectorStore

def test_settings_load_defaults():
    settings = Settings()
    assert settings.use_real_database is False
    assert settings.use_real_vector_store is False
    assert settings.llm_provider == "mock"

def test_app_state_injection_defaults():
    app = create_app()
    # Verifica se os componentes iniciais foram injetados corretamente no estado do app
    assert hasattr(app.state, "repository")
    assert isinstance(app.state.repository, InMemoryRepository)
    
    assert hasattr(app.state, "assistant_service")
    assert hasattr(app.state, "document_service")
    assert hasattr(app.state, "feedback_service")
    assert hasattr(app.state, "metrics_service")

def test_database_session_config():
    from app.infrastructure.database.session import engine
    # Verifica se o engine do SQLAlchemy foi criado (mesmo que com URL padrão)
    assert engine is not None
    assert str(engine.url).startswith("mysql+pymysql://")

def test_qdrant_client_initialization():
    from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore
    config = QdrantConfig(url="http://localhost:6333", collection="test")
    vector_store = QdrantVectorStore(config)
    # Mesmo sem o serviço rodando, o objeto deve ser criado
    assert vector_store.config.url == "http://localhost:6333"
    # O cliente pode ser None se a lib não estiver instalada, o que é esperado no ambiente de build/ci simples
    # mas o wrapper QdrantVectorStore deve existir.
    assert hasattr(vector_store, "client")

def test_main_app_respects_settings_flags(monkeypatch):
    # Simula variáveis de ambiente para forçar o uso de "real" services (embora ainda instancie mocks no main.py atual para evitar erros)
    monkeypatch.setenv("ASSISTAI_USE_REAL_DATABASE", "true")
    monkeypatch.setenv("ASSISTAI_USE_REAL_VECTOR_STORE", "true")
    
    # Limpa o cache do lru_cache para garantir que pegue as novas envs
    get_settings.cache_clear()
    
    app = create_app()
    settings = get_settings()
    
    assert settings.use_real_database is True
    assert settings.use_real_vector_store is True
    
    # Verifica se o app subiu normalmente mesmo com as flags (nosso main.py atual trata isso)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

    # Limpa o cache novamente após o teste
    get_settings.cache_clear()
