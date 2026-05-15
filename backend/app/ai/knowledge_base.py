from app.domain.models import KnowledgeDocument


SEED_DOCUMENTS = [
    KnowledgeDocument(
        id="doc-001",
        title="Procedimento de abertura de chamado",
        category="help-desk",
        tags=["chamado", "suporte", "portal"],
        content=(
            "Para abrir um chamado, acesse o portal de suporte interno, escolha a categoria do problema, "
            "descreva o impacto, anexe evidencias quando houver e envie a solicitacao. O protocolo sera "
            "gerado automaticamente e pode ser acompanhado no proprio portal."
        ),
    ),
    KnowledgeDocument(
        id="doc-002",
        title="Reset de senha corporativa",
        category="acesso",
        tags=["senha", "reset", "acesso"],
        content=(
            "Para resetar a senha, use a opcao Esqueci minha senha na tela de login corporativo. "
            "Caso nao receba o codigo de validacao, abra um chamado de acesso informando seu usuario e ramal."
        ),
    ),
    KnowledgeDocument(
        id="doc-003",
        title="Classificacao de prioridade",
        category="atendimento",
        tags=["prioridade", "incidente", "sla"],
        content=(
            "A prioridade deve considerar impacto e urgencia. Incidentes que impedem toda uma area de trabalhar "
            "devem ser classificados como alta prioridade. Duvidas individuais ou solicitacoes sem impacto imediato "
            "devem ser classificadas como baixa ou media prioridade."
        ),
    ),
    KnowledgeDocument(
        id="doc-004",
        title="Acionamento humano",
        category="handoff",
        tags=["humano", "atendente", "escalonamento"],
        content=(
            "O atendimento humano deve ser acionado quando o usuario solicitar explicitamente um atendente, "
            "quando houver urgencia operacional ou quando a base de conhecimento nao tiver informacao suficiente."
        ),
    ),
]
