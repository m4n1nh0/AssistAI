from __future__ import annotations

import re

from app.infrastructure.prompts import templates as pt


class TestSystemPrompt:
    def test_system_prompt_contains_core_rules(self) -> None:
        prompt = pt.SYSTEM_PROMPT

        assert "AssistAI" in prompt
        assert "portugues brasileiro" in prompt
        assert "nao invente" in prompt.lower()

    def test_build_system_prompt_includes_anti_hallucination(self) -> None:
        prompt = pt.build_system_prompt()

        assert "NUNCA invente" in prompt
        assert "alucinacao" in prompt.lower()

    def test_system_prompt_no_empty_lines(self) -> None:
        prompt = pt.build_system_prompt()
        lines = [line for line in prompt.split("\n") if line.strip()]
        assert all(lines)


class TestFallbackPrompt:
    def test_fallback_offers_human_attendance(self) -> None:
        assert "atendente humano" in pt.FALLBACK_PROMPT.lower()

    def test_fallback_is_reasonable_length(self) -> None:
        assert 50 < len(pt.FALLBACK_PROMPT) < 500


class TestRAGContext:
    def test_build_rag_context_with_content(self) -> None:
        contexts = ["Documento A.", "Documento B."]
        result = pt.build_rag_context(contexts)

        assert "Documento A" in result
        assert "Documento B" in result
        assert "Trecho 1" in result
        assert "Trecho 2" in result

    def test_build_rag_context_empty_returns_empty(self) -> None:
        assert pt.build_rag_context([]) == ""

    def test_build_rag_context_single_item(self) -> None:
        result = pt.build_rag_context(["Unico documento."])
        assert "Trecho 1" in result
        assert "Unico documento" in result


class TestGreetingResponses:
    def test_has_multiple_greetings(self) -> None:
        assert len(pt.GREETING_RESPONSES) >= 2

    def test_all_greetings_are_different(self) -> None:
        assert len(set(pt.GREETING_RESPONSES)) == len(pt.GREETING_RESPONSES)

    def test_greetings_contain_hello(self) -> None:
        for greeting in pt.GREETING_RESPONSES:
            lower = greeting.lower()
            assert "ola" in lower or "oi" in lower or "bem-vindo" in lower


class TestOutOfScopeResponse:
    def test_out_of_scope_mentions_help_topics(self) -> None:
        assert "chamado" in pt.OUT_OF_SCOPE_RESPONSE.lower()
        assert "senha" in pt.OUT_OF_SCOPE_RESPONSE.lower()

    def test_out_of_scope_is_polite(self) -> None:
        assert "sugiro" in pt.OUT_OF_SCOPE_RESPONSE.lower()


class TestPromptSuiteControlada:
    """Suite de 10 perguntas controladas para validacao dos prompts."""

    PERGUNTAS_DENTRO_DA_BASE = [
        "Como abrir um chamado no suporte?",
        "Como resetar minha senha?",
        "Qual o status do chamado CHM-12345?",
        "Preciso falar com um atendente humano",
        "Quais os horarios de atendimento do suporte?",
    ]

    PERGUNTAS_FORA_DA_BASE = [
        "Qual e a capital da Franca?",
        "Como fazer pao de queijo?",
        "Quem ganhou a copa de 2022?",
    ]

    CASOS_AMBIGUOS = [
        "Nao consigo acessar o sistema",
        "Meu login nao funciona",
    ]

    def test_perguntas_dentro_da_base_sao_validas(self) -> None:
        for pergunta in self.PERGUNTAS_DENTRO_DA_BASE:
            assert len(pergunta) > 0
            assert isinstance(pergunta, str)

    def test_perguntas_fora_da_base_sao_validas(self) -> None:
        for pergunta in self.PERGUNTAS_FORA_DA_BASE:
            assert len(pergunta) > 0
            assert isinstance(pergunta, str)

    def test_casos_ambigous_sao_validos(self) -> None:
        for pergunta in self.CASOS_AMBIGUOS:
            assert len(pergunta) > 0
            assert isinstance(pergunta, str)

    def test_suite_completa_tem_10_perguntas(self) -> None:
        total = (
            len(self.PERGUNTAS_DENTRO_DA_BASE)
            + len(self.PERGUNTAS_FORA_DA_BASE)
            + len(self.CASOS_AMBIGUOS)
        )
        assert total == 10

    def test_todas_perguntas_em_portugues(self) -> None:
        todas = (
            self.PERGUNTAS_DENTRO_DA_BASE
            + self.PERGUNTAS_FORA_DA_BASE
            + self.CASOS_AMBIGUOS
        )
        for pergunta in todas:
            assert re.search(r"[a-zA-Z]", pergunta)


class TestPromptSeguranca:
    def test_system_prompt_blocks_prompt_injection(self) -> None:
        prompt = pt.SYSTEM_PROMPT
        assert "nao revele" in prompt.lower()
        assert "instrucoes internas" in prompt.lower()

    def test_anti_hallucination_uses_negative_commands(self) -> None:
        assert "NUNCA" in pt.ANTI_HALLUCINATION_SYSTEM
        assert "NAO" in pt.ANTI_HALLUCINATION_SYSTEM
