# Sprint 5 — YouTube

## Objetivo

Publicar os clipes gerados pelo Content Engine no YouTube, usando a
YouTube Data API v3 com autenticação OAuth 2.0.

## Entregas

- [x] `video_metadata.py` — monta título/descrição/tags/categoria/
      privacidade a partir de um `ContentPiece`, sem depender da API
- [x] `youtube_auth.py` — fluxo OAuth 2.0 (installed-app): reutiliza e
      renova o token salvo; só abre o navegador na primeira vez que não
      há token válido
- [x] `publisher.py` — interface `VideoPublisher` (contrato)
- [x] `youtube_publisher.py` — `YouTubePublisher`, implementação concreta
      usando `googleapiclient` (upload resumível via `MediaFileUpload`)
- [x] `queue.py` — `PublishingQueue`, processa vários `ContentPiece`s
      isolando falhas por item (uma falha não trava o lote inteiro)
- [x] Testes cobrindo metadados, validação de credenciais ausentes e o
      pipeline da fila via `FakePublisher` — nenhum teste chama a API
      real do YouTube nem faz o fluxo OAuth interativo
- [x] Dependências `google-api-python-client`, `google-auth-oauthlib`,
      `google-auth-httplib2` adicionadas ao `pyproject.toml`

## Decisões técnicas

- Privacidade padrão dos vídeos publicados: `public`
- Testes usam mock (`FakePublisher`) — sem chamadas reais à API
- Autenticação: OAuth 2.0 installed-app flow, com token salvo em
  `.youtube_token.json` (não versionado) reutilizado entre execuções
- `PublishingQueue` isola falhas por item — importante para automação
  sem supervisão: um upload que falhar não impede os demais

## Configuração necessária

Para publicar de verdade (fora dos testes):
1. Criar um projeto no Google Cloud Console e habilitar a YouTube Data API v3
2. Criar credenciais OAuth 2.0 do tipo "Desktop app"
3. Preencher `YOUTUBE_CLIENT_ID` e `YOUTUBE_CLIENT_SECRET` no `.env`
4. Na primeira execução, o navegador abre para autorizar o acesso ao canal

⚠️ Recomenda-se testar primeiro com `privacy_status="private"` ou
`"unlisted"` antes de usar o padrão `"public"` em produção.

## Critério de conclusão

Uma lista de `ContentPiece`s pode ser publicada no YouTube através da
`PublishingQueue`, com metadados corretos e isolamento de falhas por
item — validado por testes automatizados que não dependem de credenciais
reais nem de chamadas de rede.
