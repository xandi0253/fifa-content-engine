# Arquitetura — FIFA Content Engine

## Visão geral

O sistema será construído em módulos independentes para permitir evolução gradual.

```text
Gravação da partida
        ↓
Ingestão de vídeo
        ↓
Processamento / FFmpeg
        ↓
Detecção de momentos
        ↓
Análise por IA
        ↓
Geração de clipes
        ↓
Título + descrição + legenda + thumbnail
        ↓
Fila de publicação
        ↓
YouTube / Instagram / TikTok
        ↓
Analytics
```

## Camadas

### 1. Video Engine
Responsável por receber, validar, cortar, converter e preparar vídeos.

### 2. AI Engine
Responsável por identificar momentos relevantes e gerar metadados de conteúdo.

### 3. Content Engine
Transforma eventos em Shorts, Reels, TikToks, posts e artigos.

### 4. Publishing Engine
Integra as plataformas oficiais e controla a fila de publicação.

### 5. Dashboard
Centraliza processamento, fila, status, erros e métricas.

### 6. Data Layer
Armazena partidas, clipes, conteúdos, publicações e métricas.

## Regra de segurança

Arquivos de vídeo, tokens, senhas e chaves de API não fazem parte do Git. O repositório contém somente código, configuração de exemplo e documentação.
