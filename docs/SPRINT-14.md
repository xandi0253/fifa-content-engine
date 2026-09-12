# Sprint 14 — Interface web local (primeira versão visual)

## Objetivo

Primeira versão de um "app" de verdade: transformar os comandos de
terminal em uma tela clicável, rodando localmente na máquina do usuário.
Sem login, sem multiusuário, sem assinatura -- só substitui
"digitar comando" por "clicar em botão".

## Contexto

Depois de validar o pipeline com dados reais (FIFA 26, Mortal Kombat 1)
e refletir sobre transformar isso num produto, a decisão foi começar
pelo menor passo visual possível: uma única tela local, sem as camadas
de conta/pagamento que um produto de assinatura precisaria.

## Entregas

- [x] `pipeline.py` (novo, na raiz do pacote) — extrai a lógica que
      antes só existia dentro de `run_pipeline.py` (script) para uma
      função de biblioteca reutilizável, `run_pipeline()`, com um
      callback `on_progress` para acompanhar o andamento em tempo real
- [x] `run_pipeline.py` reescrito como um wrapper fino de CLI sobre
      `pipeline.run_pipeline()` -- mesma funcionalidade de antes, sem
      duplicar lógica
- [x] `webapp/app.py` (novo) — servidor Flask local com:
  - `GET /` — a tela única
  - `POST /run` — inicia o pipeline em uma thread de fundo, retorna um
    job_id
  - `GET /status/<job_id>` — consulta o progresso (usado via polling
    pelo front-end, a cada 1s)
- [x] `webapp/templates/index.html` — a tela: formulário à esquerda
      (arquivo, jogo, privacidade, checkboxes), monitor de progresso em
      tempo real à direita (mostra as mensagens reais do pipeline, não
      uma animação decorativa desconectada do backend)
- [x] Identidade visual própria (não é o template genérico de SaaS):
      paleta escura inspirada em transmissão esportiva, tipografia
      condensada (Oswald) para títulos/números + Inter para o resto
- [x] Dependência `flask` adicionada ao `pyproject.toml`
- [x] Testes cobrindo: página inicial, validação de entrada, fluxo de
      sucesso, cenário "nenhum momento encontrado", captura de exceções
      inesperadas no job em background, e publicação com sucesso

## Decisões técnicas

- **Progresso em tempo real de verdade**: o "monitor" não é uma
  animação fake -- cada linha vem do mesmo `on_progress` que o CLI usa,
  então o que aparece na tela é exatamente o que está acontecendo
- **Execução em thread de fundo + polling**: mais simples que
  WebSockets/SSE para uma ferramenta local de um usuário só; suficiente
  para esse estágio
- **Caminho do vídeo como texto**, não upload de arquivo: evita a
  limitação de navegadores não exporem o caminho completo de arquivos
  selecionados, e mantém consistência com o que já era digitado no
  terminal
- **Sem persistência de jobs entre reinícios**: os jobs vivem em memória
  (`_jobs: dict`); reiniciar o servidor perde o histórico -- aceitável
  para uma ferramenta local de teste nesta fase

## O que fica para depois (fora do escopo desta sprint)

- Seleção manual de trecho (minuto X a Y) na interface -- depende da
  Sprint 13 (trimming) ser integrada aqui também
- Upload de arquivo em vez de caminho de texto
- Multiusuário, contas, autenticação, assinatura/billing
- Deploy remoto (hoje só roda `localhost`)

## Como rodar

```bash
python -m fifa_content_engine.webapp.app
```

Abre `http://127.0.0.1:5000` no navegador.

## Critério de conclusão

O pipeline pode ser configurado e executado inteiramente pela interface
web, com progresso real visível durante a execução, e o resultado
(clipe local ou link de publicação) exibido ao final -- validado por
testes automatizados e por teste manual com o servidor real rodando.
