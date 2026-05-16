# Frontend React + TypeScript

Aplicacao Web inicial do AssistAI, criada com React, TypeScript e Vite para
servir como canal principal de conversa com o assistente.

## Como executar localmente

```powershell
cd frontend
npm install
npm run dev
```

Por padrao, o Vite sobe em `http://localhost:5173`.

Para gerar build de producao:

```powershell
npm run build
```

## Configuracao

As variaveis do frontend usam prefixo `VITE_`:

| Variavel | Padrao | Uso |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | URL base da API FastAPI. |
| `VITE_WEB_USER_ID` | `web-user-001` | Usuario tecnico usado no canal Web da POC. |

## Camadas

| Caminho | Responsabilidade |
|---|---|
| `src/main.tsx` | Ponto de entrada React. |
| `src/presentation` | Shell visual, paginas e componentes. |
| `src/application` | Hooks e configuracoes de uso da aplicacao. |
| `src/domain` | Contratos TypeScript alinhados ao backend. |
| `src/infrastructure` | Clientes HTTP e adaptadores externos. |
| `src/shared` | Helpers reutilizaveis. |

## Fluxo inicial

1. `ChatPage` captura a pergunta do usuario.
2. `useChat` controla estado de mensagens, loading, erro e feedback.
3. `apiClient.ask` chama `POST /ask` com `channel = "web"`.
4. A resposta do assistente e exibida com fontes e botoes de feedback.
5. `apiClient.sendFeedback` envia a avaliacao para `POST /feedback`.

## Telas iniciais

| Tela | Objetivo |
|---|---|
| Chat | Conversar com o assistente pela Web. |
| Historico | Consultar atendimentos registrados pela API. |
| Documentos | Visualizar documentos disponiveis para RAG. |
| Indicadores | Visualizar metricas basicas da POC. |
