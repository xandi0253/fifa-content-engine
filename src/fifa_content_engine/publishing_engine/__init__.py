"""Publishing Engine.

Integra as plataformas oficiais (YouTube, Instagram, TikTok) e controla
a fila de publicação de conteúdo. YouTube (Sprint 5), Instagram (Sprint
6) e TikTok (Sprint 7) implementados — ver youtube_publisher.YouTubePublisher,
instagram_publisher.InstagramPublisher e tiktok_publisher.TikTokPublisher.

Instagram e TikTok requerem um MediaHoster (ver media_hosting.py) para
expor o clipe em uma URL pública antes de publicar — nenhuma
implementação concreta de hospedagem é fornecida ainda, é um ponto de
extensão.
"""
