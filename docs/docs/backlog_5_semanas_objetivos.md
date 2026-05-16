# Backlog de Desenvolvimento — Assistente de Atendimento Inteligente

## Objetivo do documento

Este documento organiza o **MVP + backlog principal** do projeto **Assistente de Atendimento Inteligente** em um plano de execução de **5 semanas**, considerando um time de **10 desenvolvedores trabalhando em conjunto**.

Cada tarefa possui um objetivo claro, contextualizado com o propósito do projeto: construir um assistente capaz de atender usuários via Web e Telegram, consultar uma base de conhecimento, responder com apoio de IA/RAG, registrar histórico, coletar feedback, aplicar fallback e permitir evolução futura com integrações controladas.

---

## Visão geral do plano

| Semana | Foco | Entrega principal |
|---|---|---|
| Semana 1 | Fundação técnica + RAG inicial | API, ambiente, Qdrant, ingestão e busca semântica |
| Semana 2 | MVP Web funcional | Chat Web com RAG, histórico, fallback e feedback |
| Semana 3 | Telegram + LangGraph + segurança básica | Multicanalidade e fluxo controlado |
| Semana 4 | Base administrável + métricas | Gestão simples de documentos e indicadores |
| Semana 5 | Qualidade + MCP simulado + fechamento | Testes, Sonar, integração simulada e relatório final |

---

## Organização sugerida do time

| Frente | Quantidade | Responsabilidade |
|---|---:|---|
| IA/RAG | 2 devs | Qdrant, embeddings, prompt, fallback e LangGraph |
| Backend | 3 devs | FastAPI, MySQL, contratos, persistência e APIs |
| Frontend | 2 devs | Chat Web, histórico, feedback e telas administrativas simples |
| Integrações | 1 dev | Telegram e MCP simulado |
| QA/DevEx | 1 dev | Pytest, Sonar, testes de contrato e testes de prompt |
| Tech Lead/Arquitetura | 1 dev | Decisões técnicas, revisão, integração e desbloqueio do time |

---

# Semana 1 — Fundação técnica + RAG inicial

## Objetivo da semana

Criar a base técnica do projeto e validar o risco principal: **o assistente consegue buscar informações na base de conhecimento e recuperar contexto relevante?**

## Resultado esperado

Ao final da semana, o backend deve possuir um endpoint funcional que recebe uma pergunta e retorna os trechos mais relevantes recuperados da base vetorial.

---

## Tarefas da Semana 1

| Código | Nome da tarefa | Objetivo |
|---|---|---|
| S1-01 | Definir contrato oficial de pergunta e resposta do assistente | Padronizar a comunicação entre Web, Telegram, API e motor de IA, evitando retrabalho entre as frentes de desenvolvimento. |
| S1-02 | Criar estrutura inicial do backend FastAPI | Preparar a API central do projeto, criando a base para receber mensagens, processar solicitações e integrar com IA, banco relacional e banco vetorial. |
| S1-03 | Criar estrutura inicial do frontend React + TypeScript | Preparar a aplicação Web que será usada pelo usuário para conversar com o assistente. |
| S1-04 | Subir ambiente local com MySQL e Qdrant | Garantir que todos os devs tenham um ambiente reproduzível para persistência transacional e busca vetorial. |
| S1-05 | Criar modelo inicial de atendimento, mensagem e feedback | Definir as entidades mínimas para registrar conversas, respostas, avaliações e rastreabilidade do atendimento. |
| S1-06 | Definir base inicial de conhecimento de suporte interno | Selecionar conteúdos simples e controlados para validar o RAG com perguntas objetivas e respostas verificáveis. |
| S1-07 | Implementar loader de documentos da base | Permitir que documentos em Markdown, JSON ou TXT sejam carregados para o pipeline de ingestão. |
| S1-08 | Implementar chunking dos documentos | Quebrar documentos em trechos menores para melhorar a busca semântica e a precisão das respostas. |
| S1-09 | Gerar embeddings e indexar no Qdrant | Transformar os trechos da base de conhecimento em vetores pesquisáveis pelo motor de RAG. |
| S1-10 | Criar endpoint `/ask` com busca semântica inicial | Validar o fluxo pergunta → busca vetorial → retorno de contexto, mesmo antes da resposta final com LLM. |
| S1-11 | Criar testes iniciais de contrato da API | Garantir que a estrutura de entrada e saída da API esteja estável para frontend, Telegram e testes. |
| S1-12 | Criar checklist de PR, branch e padrão de commit | Organizar a colaboração entre os 10 devs, reduzindo conflitos, retrabalho e inconsistência de código. Veja [Checklist de Contribuição](../contribution_checklist.md) para regras e boas práticas. |

## Critério de pronto da Semana 1

```text
Pergunta enviada para API
→ API consulta Qdrant
→ Qdrant retorna trechos relevantes
→ resposta técnica mostra contexto recuperado
```

---

# Semana 2 — MVP Web funcional

## Objetivo da semana

Transformar a busca semântica inicial em uma experiência real de uso pela Web, com resposta gerada por IA e controle de fallback.

## Resultado esperado

Ao final da semana, o usuário deve conseguir conversar com o assistente pela interface Web, receber resposta baseada na documentação, avaliar a resposta e ter o histórico salvo.

---

## Tarefas da Semana 2

| Código | Nome da tarefa | Objetivo |
|---|---|---|
| S2-01 | Integrar LLM ao endpoint `/ask` | Permitir que o sistema gere uma resposta em linguagem natural a partir do contexto recuperado no Qdrant. |
| S2-02 | Criar prompt base com regras de resposta | Definir tom, formato, restrições de uso da base, comportamento contra alucinação e padrão de fallback. |
| S2-03 | Implementar resposta baseada exclusivamente no contexto | Garantir que o assistente responda apenas quando houver informação suficiente nos documentos recuperados. |
| S2-04 | Implementar fallback para ausência de contexto confiável | Fazer o assistente informar que não encontrou base suficiente quando a pergunta não puder ser respondida com segurança. |
| S2-05 | Definir score mínimo de relevância do Qdrant | Estabelecer um limite técnico para decidir se o contexto recuperado é confiável o suficiente para gerar resposta. |
| S2-06 | Persistir pergunta, resposta, score e fontes no MySQL | Garantir rastreabilidade, auditoria e análise futura das interações realizadas com o assistente. |
| S2-07 | Criar tela de chat Web | Disponibilizar uma interface simples para o usuário enviar perguntas e visualizar respostas. |
| S2-08 | Integrar tela Web ao endpoint `/ask` | Fechar o fluxo Web → API → IA/RAG → resposta ao usuário. |
| S2-09 | Implementar loading e renderização de mensagens | Melhorar a experiência de uso durante o processamento das respostas. |
| S2-10 | Criar botão de feedback útil/não útil | Permitir que o usuário avalie a qualidade da resposta recebida. |
| S2-11 | Persistir feedback vinculado à resposta | Relacionar cada avaliação do usuário à resposta gerada, permitindo análise de qualidade. |
| S2-12 | Criar testes de pergunta conhecida e pergunta fora da base | Validar os dois cenários mais importantes da POC: resposta correta e fallback seguro. |

## Critério de pronto da Semana 2

```text
Usuário pergunta pela Web
→ sistema busca contexto no Qdrant
→ LLM responde com base na documentação
→ histórico é salvo
→ usuário avalia a resposta
→ fallback funciona quando não há base suficiente
```

## Marco da Semana 2

Ao final da Semana 2, o projeto deve possuir o **MVP técnico Web**.

---

# Semana 3 — Telegram + LangGraph + segurança básica

## Objetivo da semana

Expandir o atendimento para Telegram e organizar o comportamento do assistente em um fluxo controlado de decisão.

## Resultado esperado

O mesmo motor de IA deve atender Web e Telegram, reutilizando o fluxo central de processamento, com classificação inicial de intenção, validação de escopo e segurança básica.

---

## Tarefas da Semana 3

| Código | Nome da tarefa | Objetivo |
|---|---|---|
| S3-01 | Criar bot Telegram do assistente | Abrir um canal alternativo de atendimento para validar multicanalidade. |
| S3-02 | Implementar webhook de recebimento do Telegram | Permitir que mensagens enviadas ao bot sejam recebidas pelo backend. |
| S3-03 | Reutilizar endpoint `/ask` para mensagens do Telegram | Evitar duplicação de lógica e garantir que Web e Telegram usem o mesmo motor de IA/RAG. |
| S3-04 | Persistir canal de origem Web/Telegram | Registrar de onde veio cada atendimento para análise e rastreabilidade. |
| S3-05 | Criar resposta padrão para solicitação de humano | Tratar de forma controlada os casos em que o usuário deseja atendimento humano. |
| S3-06 | Marcar atendimento como escalonado | Registrar que uma conversa precisa de intervenção humana ou continuidade fora da automação. |
| S3-07 | Mapear fluxo oficial do assistente em estados | Formalizar as etapas de entrada, intenção, escopo, busca, resposta, fallback e persistência. |
| S3-08 | Implementar fluxo inicial com LangGraph | Organizar a orquestração da conversa como um fluxo previsível e evolutivo. |
| S3-09 | Criar etapa de classificação de intenção | Diferenciar perguntas simples, procedimentos, saudações, solicitações humanas e temas fora de escopo. |
| S3-10 | Criar etapa de validação de escopo | Evitar que o assistente responda perguntas fora do domínio definido para a POC. |
| S3-11 | Implementar sanitização de entrada do usuário | Reduzir riscos causados por entradas malformadas, excessivas ou potencialmente perigosas. |
| S3-12 | Implementar proteção básica contra prompt injection | Reduzir a chance de o usuário manipular instruções internas ou forçar o assistente a ignorar regras. |
| S3-13 | Criar testes Web e Telegram usando o mesmo fluxo | Validar que ambos os canais funcionam com a mesma lógica central de atendimento. |

## Critério de pronto da Semana 3

```text
Mensagem Web e Telegram
→ passam pelo mesmo fluxo de IA
→ intenção é identificada
→ contexto é recuperado
→ resposta ou fallback é retornado
→ histórico registra canal e metadados
```

---

# Semana 4 — Base de conhecimento administrável + métricas

## Objetivo da semana

Dar governança mínima à base de conhecimento e criar métricas para avaliar a qualidade e operação do assistente.

## Resultado esperado

O time deve conseguir cadastrar, listar, ativar/inativar documentos, reindexar a base e visualizar indicadores simples de uso e qualidade.

---

## Tarefas da Semana 4

| Código | Nome da tarefa | Objetivo |
|---|---|---|
| S4-01 | Criar endpoint para cadastrar documento | Permitir que novos conteúdos sejam adicionados à base de conhecimento de forma controlada. |
| S4-02 | Criar endpoint para listar documentos | Dar visibilidade aos documentos disponíveis na base de conhecimento. |
| S4-03 | Criar status ativo/inativo para documentos | Impedir que conteúdos obsoletos ou não aprovados sejam usados pelo RAG. |
| S4-04 | Criar versionamento simples de documento | Rastrear qual versão do conteúdo foi utilizada para gerar cada resposta. |
| S4-05 | Criar rotina de reindexação manual | Atualizar os vetores no Qdrant após alteração ou inclusão de documentos. |
| S4-06 | Criar tela simples de documentos | Permitir consulta visual da base cadastrada pela interface Web. |
| S4-07 | Criar tela simples de cadastro/upload | Facilitar a curadoria da base de conhecimento sem depender apenas de scripts técnicos. |
| S4-08 | Garantir que documento inativo não entre no RAG | Reforçar a governança e evitar respostas baseadas em conteúdo inválido. |
| S4-09 | Registrar tempo médio de resposta | Medir a performance conversacional do assistente. |
| S4-10 | Registrar taxa de fallback | Identificar lacunas na base de conhecimento e medir a incapacidade de resposta. |
| S4-11 | Registrar documentos mais utilizados | Identificar quais conteúdos são mais relevantes nas respostas geradas. |
| S4-12 | Criar tela simples de indicadores | Disponibilizar uma visão mínima de operação e qualidade do assistente. |
| S4-13 | Criar listagem de perguntas sem resposta | Alimentar o processo de melhoria contínua da base de conhecimento. |
| S4-14 | Testar alteração de documento e nova resposta | Validar o ciclo completo de curadoria: cadastrar, indexar, perguntar e responder com a nova informação. |

## Critério de pronto da Semana 4

```text
Documento é cadastrado
→ documento é indexado
→ assistente usa o novo conteúdo
→ resposta registra fonte e versão
→ métricas básicas aparecem na interface
```

---

# Semana 5 — Qualidade, MCP simulado e fechamento da POC

## Objetivo da semana

Fechar a POC com evidências técnicas, testes, análise de qualidade, relatório final e uma integração externa simulada.

## Resultado esperado

A POC deve terminar demonstrável e mensurável, contendo Web, Telegram, RAG, histórico, feedback, fallback, LangGraph, base administrável, métricas, testes e MCP simulado.

---

## Tarefas da Semana 5

| Código | Nome da tarefa | Objetivo |
|---|---|---|
| S5-01 | Definir contrato de ferramenta externa | Padronizar como o assistente poderá consultar sistemas externos de forma segura e previsível. |
| S5-02 | Criar ferramenta simulada de consulta de chamado | Demonstrar capacidade de integração sem depender de um sistema corporativo real. |
| S5-03 | Integrar ferramenta simulada ao fluxo do assistente | Validar que o assistente consegue usar uma ferramenta externa controlada durante o atendimento. |
| S5-04 | Criar allowlist de ferramentas permitidas | Impedir execução livre ou uso de ferramentas não autorizadas pelo assistente. |
| S5-05 | Registrar logs de uso da ferramenta | Garantir auditoria das chamadas realizadas a integrações externas. |
| S5-06 | Criar fallback para falha da ferramenta | Manter a conversa estável mesmo quando a ferramenta externa simulada falhar. |
| S5-07 | Ampliar testes unitários dos serviços principais | Aumentar a confiabilidade das regras e serviços centrais do backend. |
| S5-08 | Criar testes de integração com MySQL e Qdrant | Validar o funcionamento real das dependências principais de persistência e busca vetorial. |
| S5-09 | Criar testes simulados para Telegram | Validar o canal Telegram sem depender de testes manuais constantes. |
| S5-10 | Criar testes de prompt com perguntas controladas | Medir se o assistente responde corretamente, aplica fallback e evita respostas inventadas. |
| S5-11 | Executar análise com Sonar | Identificar bugs, code smells, duplicidades e vulnerabilidades críticas. |
| S5-12 | Medir acurácia em perguntas conhecidas | Avaliar se o assistente atinge a meta de responder corretamente a perguntas cobertas pela base. |
| S5-13 | Medir fallback em perguntas fora da base | Validar se o assistente evita alucinação quando não há base suficiente. |
| S5-14 | Corrigir bugs críticos encontrados nos testes | Estabilizar a entrega final antes da demonstração e avaliação da POC. |
| S5-15 | Gerar relatório final da POC | Consolidar resultados técnicos, métricas, evidências, riscos e próximos passos. |
| S5-16 | Documentar backlog pós-POC | Separar claramente o que foi entregue, o que ficou pendente e o que deve evoluir após a POC. |

## Critério de pronto da Semana 5

```text
POC demonstrável
→ Web funcionando
→ Telegram funcionando
→ RAG funcionando
→ fallback funcionando
→ histórico e feedback funcionando
→ base administrável funcionando
→ MCP simulado funcionando
→ testes principais executados
→ relatório final produzido
```

---

# Priorização das entregas em 5 semanas

## Obrigatório

| Item | Justificativa |
|---|---|
| API `/ask` | É o ponto central de entrada do assistente. |
| RAG com Qdrant | É o principal valor técnico da POC. |
| LLM com prompt controlado | Permite resposta conversacional com governança. |
| Web Chat | É o canal principal de validação com usuário. |
| Histórico | Garante rastreabilidade dos atendimentos. |
| Feedback | Mede qualidade percebida da resposta. |
| Fallback | Reduz risco de alucinação. |
| Telegram | Valida multicanalidade. |
| LangGraph | Organiza o fluxo de decisão do assistente. |
| Base administrável simples | Permite evolução da base sem depender apenas do código. |
| Métricas básicas | Permite avaliar uso e qualidade. |
| Testes principais | Dá segurança mínima para a entrega. |
| Relatório final | Consolida evidências da POC. |

## Desejável

| Item | Justificativa |
|---|---|
| Sonar completo | Melhora a visibilidade de qualidade técnica. |
| Coverage próximo de 80% | É uma meta importante, mas pode ser progressiva na POC. |
| Dashboard mais refinado | Ajuda na apresentação, mas não é obrigatório para provar a arquitetura. |
| MCP simulado | Demonstra expansão futura, mas não deve bloquear o MVP. |

## Fora do escopo das 5 semanas

| Item | Motivo |
|---|---|
| PyTorch | Não é necessário para validar o assistente RAG. |
| Treinamento próprio de modelo | Alto custo e baixo valor para a POC inicial. |
| Fine-tuning | Não é necessário antes de validar RAG e prompt. |
| SSO corporativo | Complexidade desnecessária para a POC. |
| Integrações reais com sistemas internos | Devem ser substituídas por simulação controlada. |
| Painel administrativo completo | Uma tela simples é suficiente para a POC. |
| Observabilidade avançada | Logs e métricas básicas atendem ao objetivo inicial. |
| Alta disponibilidade | Não é requisito de POC. |
| Analytics avançado | Pode entrar após validação do MVP. |
| Workflow completo de help desk | O suficiente é registrar escalonamento simples. |

---

# Marcos do projeto

| Semana | Marco |
|---|---|
| Semana 1 | RAG técnico inicial funcionando |
| Semana 2 | MVP Web finalizado |
| Semana 3 | Multicanalidade + fluxo controlado |
| Semana 4 | Governança da base + métricas |
| Semana 5 | POC fechada com qualidade e relatório |

---

# Conclusão

O plano de 5 semanas é agressivo, mas viável com 10 devs desde que o time trabalhe com entregas integradas e priorize o fluxo principal do produto.

A regra central do projeto deve ser:

```text
Não construir camadas isoladas.
Construir entregas verticais e demonstráveis toda semana.
```

O foco da POC é validar:

```text
Usuário pergunta
→ assistente busca conhecimento
→ IA responde com base em contexto
→ sistema registra histórico
→ usuário avalia
→ fallback evita resposta inventada
→ métricas orientam melhoria contínua
```