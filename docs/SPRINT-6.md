# Sprint 6 — Instagram

## Objetivo

Publicar os clipes gerados pelo Content Engine no Instagram (Reels),
usando a Instagram Graph API.

## Entregas

- [x] `media_hosting.py` — interface `MediaHoster` (contrato): expõe um
      clipe local em uma URL pública. **Sem implementação concreta ainda**
      — ponto de extensão plugável, a hospedagem real fica para configurar
      depois (S3, Cloudflare R2, etc.)
- [x] `instagram_client.py` — wrapper fino da Instagram Graph API:
      criação de contêiner de mídia, consulta de status, publicação e
      busca do permalink
- [x] `instagram_publisher.py` — `InstagramPublisher`, implementação
      concreta de `VideoPublisher`: hospeda o clipe (via `MediaHoster`),
      cria o contêiner, aguarda o processamento (polling) e publica
- [x] Testes cobrindo o cliente da Graph API, o publisher (fluxo de
      sucesso, erro de processamento, timeout de polling) e a interface
      `MediaHoster` — nenhum teste chama a API real do Instagram
- [x] Dependência `requests` adicionada ao `pyproject.toml`

## Decisões técnicas

- **Hospedagem de mídia é plugável**: a API do Instagram exige uma URL
  pública (diferente do YouTube, que aceita upload direto). Esta sprint
  define o contrato (`MediaHoster`) mas não implementa nenhum provedor
  concreto — isso fica para quando a hospedagem for escolhida/configurada
- Testes usam mock — sem chamadas reais à API do Instagram
- Fluxo de publicação segue o padrão da Graph API: criar contêiner →
  aguardar status `FINISHED` (com timeout configurável) → publicar →
  buscar permalink

## Configuração necessária

Para publicar de verdade (fora dos testes):
1. Conta Instagram Business ou Creator, vinculada a uma Página do Facebook
2. Um app no Meta for Developers com acesso à Instagram Graph API
3. Preencher `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_BUSINESS_ACCOUNT_ID` no `.env`
4. Implementar um `MediaHoster` concreto (ex: subir o clipe para S3/R2 e
   retornar a URL pública) e passá-lo ao construir o `InstagramPublisher`

## Critério de conclusão

Um `ContentPiece` pode ser publicado no Instagram através do
`InstagramPublisher`, desde que um `MediaHoster` concreto seja fornecido
— validado por testes automatizados que não dependem de credenciais
reais nem de chamadas de rede.
