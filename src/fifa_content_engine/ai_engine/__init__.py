"""AI Engine.

Responsável por identificar momentos relevantes das partidas e gerar
metadados de conteúdo (títulos, descrições, tags). Ver
analyzer.AIMomentAnalyzer para a implementação, que usa a OpenAI
(openai_classifier.OpenAIFrameClassifier) para classificar frames
extraídos dos timestamps candidatos.
"""
