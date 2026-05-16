# Checklist de Contribuição

## 1. Estratégia de branch
- branch principal: `main` (ou `master`).
- crie branches de funcionalidade a partir de `main`.
- naming sugerido:
  - `feature/S1-08-carregar-documentos`
  - `fix/S1-10-ajustar-endpoint-ask`
  - `chore/S1-12-checklist-contribuicao`
  - `docs/S1-12-atualizar-readme`
- mantenha cada branch focada em um objetivo claro e limitado.
- sincronize frequentemente com `main` antes de abrir o PR.

## 2. Checklist de Pull Request
- [ ] Branch baseada em `main` e atualizada antes do merge.
- [ ] Título do PR claro e objetivo.
- [ ] Descrição do PR com:
  - problema ou objetivo;
  - resumo das mudanças;
  - resultados esperados;
  - links para issues ou tarefas relacionadas.
- [ ] Conteúdo limitado a uma entrega coesa.
- [ ] Testes adicionados ou atualizados quando pertinente.
- [ ] Código revisado pelo autor antes do envio.
- [ ] Documentação atualizada se houver mudança de comportamento, API, configuração ou uso.
- [ ] Verificação manual dos pontos principais:
  - backend: endpoints, serviços e fluxo de dados;
  - frontend: navegação, exibição e validação de entrada;
  - integração: dados persistidos e respostas esperadas.
- [ ] Confirmação de que não há dados sensíveis acidentalmente incluídos.
- [ ] Mudanças no Docker ou ambiente local documentadas.
- [ ] Comentários de código removidos ou convertidos em documentação quando relevantes.

## 3. Padrão de commit
- use verbos no imperativo e o escopo quando fizer sentido.
- exemplos:
  - `feat(rag): implementar chunking de documentos`
  - `fix(api): corrigir rota /ask com roteador global`
  - `docs: adicionar checklist de contribuição`
  - `test: criar teste de contrato para /documents/reindex`
  - `chore: atualizar dependências do backend`
- evite commits gigantes; prefira pequenas alterações atômicas.
- sempre escreva mensagens de commit claras e descritivas.

## 4. Requisitos de qualidade
- [ ] Novo código coberto por testes unitários quando possível.
- [ ] API com contratos bem definidos e testes de contrato.
- [ ] No mínimo um teste de integração para fluxos críticos.
- [ ] Confirme estilo e lint se houver regras configuradas.
- [ ] Logs e mensagens de erro claros para diagnóstico.
- [ ] Reuso de componentes e serviços preferido em vez de duplicação.

## 5. Revisão e merge
- solicite pelo menos uma revisão de outro membro do time.
- verifique comentários e ajuste o PR antes de merge.
- garanta que o PR esteja verde em checks e testes relevantes.
- use `merge` ou `squash merge` conforme política do time.

## 6. Comunicação e rastreabilidade
- vincule o PR à tarefa / backlog correspondente.
- adicione contexto sobre alterações arquiteturais importantes.
- mantenha o histórico de commits legível e rastreável.
- atualize `docs/` quando o comportamento do projeto mudar.
