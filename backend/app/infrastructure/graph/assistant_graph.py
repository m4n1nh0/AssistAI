from __future__ import annotations

import logging
import re
from time import perf_counter
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.core.config import Settings
from app.domain.contracts import AskResponse, SourceResponse
from app.domain.enums import Channel, Intent
from app.domain.models import AiLog, MessageRecord, Source, new_id
from app.domain.protocols import LLMGateway, Repository, Retriever
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.prompts import templates as pt

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    user_message: str
    user_id: str
    channel: str
    sanitized_message: str
    intent: str
    confidence: float
    fallback: bool
    answer: str
    sources: list[dict[str, Any]]
    source_document_ids: list[str]
    elapsed_ms: int
    user: Any
    attendance: Any
    contexts: list
    message_record: Any


def _sanitize(state: GraphState) -> dict[str, Any]:
    raw = state["user_message"]
    return {"sanitized_message": " ".join(raw.strip().split())}


def _classify(state: GraphState) -> dict[str, Any]:
    lower = state["sanitized_message"].lower()
    if any(term in lower for term in ["humano", "atendente", "pessoa"]):
        return {"intent": Intent.HUMAN_REQUEST.value}
    if re.search(r"\bchm-\d+\b", lower):
        return {"intent": Intent.TICKET_STATUS.value}
    if lower in {"oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"}:
        return {"intent": Intent.GREETING.value}
    return {"intent": Intent.PROCEDURE.value}


class AssistantGraph:
    def __init__(
        self,
        repository: Repository,
        retriever: Retriever,
        llm_gateway: LLMGateway,
        tools: SimulatedToolRegistry,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.retriever = retriever
        self.llm_gateway = llm_gateway
        self.tools = tools
        self.settings = settings
        self._graph = self._build()

    def _setup_user(self, state: GraphState) -> dict[str, Any]:
        user = self.repository.find_or_create_user(
            state["user_id"], Channel(state["channel"])
        )
        return {"user": user}

    def _setup_attendance(self, state: GraphState) -> dict[str, Any]:
        att = self.repository.create_attendance(
            state["user"].id, Channel(state["channel"])
        )
        return {"attendance": att}

    def _retrieve(self, state: GraphState) -> dict[str, Any]:
        contexts = self.retriever.search(
            state["sanitized_message"], top_k=self.settings.rag_top_k
        )
        return {"contexts": contexts}

    def _filter(self, state: GraphState) -> dict[str, Any]:
        contexts = [
            ctx
            for ctx in state["contexts"]
            if ctx.score >= self.settings.min_relevance_score
        ]
        confidence = contexts[0].score if contexts else 0.0
        return {"contexts": contexts, "confidence": confidence}

    def _router(self, state: GraphState) -> str:
        intent = state["intent"]
        if intent == Intent.GREETING.value:
            return "greeting"
        if intent == Intent.HUMAN_REQUEST.value:
            return "human_request"
        if intent == Intent.TICKET_STATUS.value:
            return "ticket"
        if state["contexts"]:
            return "has_context"
        return "no_context"

    def _respond_greeting(self, state: GraphState) -> dict[str, Any]:
        return {
            "answer": (
                "Ola! Como posso ajudar? Sou o assistente virtual de "
                "suporte interno. Pergunte sobre abertura de chamados, "
                "reset de senha ou consulta de status."
            ),
            "fallback": False,
            "confidence": 1.0,
        }

    def _respond_human(self, state: GraphState) -> dict[str, Any]:
        return {
            "answer": (
                "Entendi que voce precisa de atendimento humano. "
                "Marquei este atendimento para escalonamento."
            ),
            "fallback": True,
            "confidence": 1.0,
        }

    def _respond_ticket(self, state: GraphState) -> dict[str, Any]:
        match = re.search(
            r"\b(CHM-\d+)\b",
            state["sanitized_message"],
            flags=re.IGNORECASE,
        )
        if not match:
            return {
                "answer": (
                    "Informe o numero do chamado no formato CHM-12345 "
                    "para consulta."
                ),
                "fallback": False,
                "confidence": 0.75,
            }

        ticket_id = match.group(1).upper()
        result = self.tools.ticket_status(ticket_id)
        output = result.output_payload
        answer = (
            f"O chamado {output.get('ticket_id', ticket_id)} esta "
            f"{output.get('status', 'indisponivel')}. "
            f"Ultima atualizacao: "
            f"{output.get('last_update', 'sem registro')}."
        )
        return {
            "answer": answer,
            "fallback": False,
            "confidence": 0.9 if result.success else 0.3,
        }

    def _generate_with_context(self, state: GraphState) -> dict[str, Any]:
        system_prompt = pt.build_system_prompt()
        answer = self.llm_gateway.generate(
            state["sanitized_message"],
            state["contexts"],
            system_prompt=system_prompt,
        )
        return {"answer": answer, "fallback": False}

    def _respond_fallback(self, state: GraphState) -> dict[str, Any]:
        return {
            "answer": pt.FALLBACK_PROMPT,
            "fallback": True,
            "confidence": 0.0,
        }

    def _persist(self, state: GraphState) -> dict[str, Any]:
        started = perf_counter()
        sources = self._build_sources(state["contexts"])

        message_record = MessageRecord(
            id=new_id("msg"),
            attendance_id=state["attendance"].id,
            user_message=state["sanitized_message"],
            assistant_answer=state["answer"],
            fallback=state["fallback"],
            intent=Intent(state["intent"]),
            confidence=round(state["confidence"], 4),
            sources=sources,
        )
        self.repository.add_message(message_record)

        source_ids = [s.document_id for s in sources]

        if state["fallback"]:
            reason = (
                "Usuario solicitou atendimento humano."
                if state["intent"] == Intent.HUMAN_REQUEST.value
                else "Contexto insuficiente para resposta."
            )
            self.repository.mark_attendance_escalated(
                state["attendance"].id, reason=reason,
            )

        elapsed_ms = round((perf_counter() - started) * 1000)
        self.repository.add_ai_log(
            AiLog(
                id=new_id("ailog"),
                message_id=message_record.id,
                intent=Intent(state["intent"]),
                relevance_score=round(state["confidence"], 4),
                fallback=state["fallback"],
                source_document_ids=source_ids,
                elapsed_ms=elapsed_ms,
            )
        )

        logger.info(
            "Graph: intent=%s fallback=%s confidence=%.2f elapsed=%dms",
            state["intent"],
            state["fallback"],
            state["confidence"],
            elapsed_ms,
        )

        return {
            "message_record": message_record,
            "sources": [
                {
                    "document_id": s.document_id,
                    "title": s.title,
                    "version": s.version,
                    "score": s.score,
                }
                for s in sources
            ],
            "elapsed_ms": elapsed_ms,
        }

    def _build_sources(self, contexts: list) -> list[Source]:
        from app.domain.models import RetrievalResult

        sources: list[Source] = []
        for ctx in contexts:
            if not isinstance(ctx, RetrievalResult):
                continue
            doc = self.repository.get_document(ctx.chunk.document_id)
            if not doc:
                continue
            sources.append(
                Source(
                    document_id=doc.id,
                    title=doc.title,
                    version=doc.version,
                    score=ctx.score,
                )
            )
        return sources

    def _build(self) -> Any:
        builder = StateGraph(GraphState)

        builder.add_node("sanitize", _sanitize)
        builder.add_node("classify", _classify)
        builder.add_node("setup_user", self._setup_user)
        builder.add_node("setup_attendance", self._setup_attendance)
        builder.add_node("retrieve", self._retrieve)
        builder.add_node("filter", self._filter)
        builder.add_node("greeting", self._respond_greeting)
        builder.add_node("human_request", self._respond_human)
        builder.add_node("ticket", self._respond_ticket)
        builder.add_node("has_context", self._generate_with_context)
        builder.add_node("no_context", self._respond_fallback)
        builder.add_node("persist", self._persist)

        builder.add_edge(START, "sanitize")
        builder.add_edge("sanitize", "classify")
        builder.add_edge("classify", "setup_user")
        builder.add_edge("setup_user", "setup_attendance")
        builder.add_edge("setup_attendance", "retrieve")
        builder.add_edge("retrieve", "filter")

        builder.add_conditional_edges(
            "filter",
            self._router,
            {
                "greeting": "greeting",
                "human_request": "human_request",
                "ticket": "ticket",
                "has_context": "has_context",
                "no_context": "no_context",
            },
        )

        for node in (
            "greeting",
            "human_request",
            "ticket",
            "has_context",
            "no_context",
        ):
            builder.add_edge(node, "persist")

        builder.add_edge("persist", END)
        return builder.compile()

    def run(
        self,
        message: str,
        user_id: str,
        channel: Channel,
    ) -> AskResponse:
        initial: GraphState = {
            "user_message": message,
            "user_id": user_id,
            "channel": channel.value,
            "sanitized_message": "",
            "intent": "",
            "confidence": 0.0,
            "fallback": False,
            "answer": "",
            "sources": [],
            "source_document_ids": [],
            "elapsed_ms": 0,
            "user": None,
            "attendance": None,
            "contexts": [],
            "message_record": None,
        }

        result = self._graph.invoke(initial)

        attendance_id = ""
        if result.get("attendance"):
            attendance_id = result["attendance"].id

        message_id = ""
        if result.get("message_record"):
            message_id = result["message_record"].id

        return AskResponse(
            answer=result.get("answer", ""),
            fallback=result.get("fallback", False),
            intent=Intent(result.get("intent", "desconhecida")),
            confidence=round(result.get("confidence", 0.0), 4),
            sources=[
                SourceResponse(**s) for s in result.get("sources", [])
            ],
            attendance_id=attendance_id,
            message_id=message_id,
        )
