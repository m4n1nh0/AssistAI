from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.infrastructure.rag.simple_retriever import RetrievalResult


class LangChainLLMGateway:
    def __init__(
        self,
        provider: str = "ollama",
        model_name: str = "llama-3.1-8b-instant",
        api_key: str | None = None,
    ) -> None:
        self.provider = provider

        if provider == "groq":
            self.llm = ChatGroq(
                model=model_name,
                api_key=api_key,
                temperature=0.0,
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                temperature=0.0,
            )
        else:
            # ollama ou qualquer outro → local
            self.llm = ChatOllama(
                model=model_name,
                base_url="http://host.docker.internal:11434",
                temperature=0.0,
            )

        self.system_prompt = (
            "Você é um assistente de suporte técnico. Responda única e exclusivamente "
            "com base nos documentos de contexto fornecidos.\n\n"
            "Regras:\n"
            "1. Se o contexto não contiver a resposta, diga EXATAMENTE: "
            "'Não encontrei base suficiente para responder com segurança. "
            "Posso encaminhar este atendimento para um humano.'\n"
            "2. Não invente informações.\n"
            "3. O formato da resposta deve ser direto e amigável.\n\n"
            "Contexto:\n"
            "{context}"
        )

    def generate(self, question: str, contexts: list[RetrievalResult]) -> str:
        ctx_texts = []
        for c in contexts:
            title_str = f"Título: {c.chunk.metadata.get('title', 'Sem título')}"
            ctx_texts.append(f"{title_str}\nTexto: {c.chunk.content}")

        combined_context = "\n\n---\n\n".join(ctx_texts)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}"),
        ])

        chain = prompt_template | self.llm

        try:
            response = chain.invoke({"context": combined_context, "question": question})
            return response.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return (
                "Não encontrei base suficiente para responder com segurança. "
                "Posso encaminhar este atendimento para um humano."
            )
