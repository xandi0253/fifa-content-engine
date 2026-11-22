# Estúdio de futebol 3D

Protótipo para avaliar um voleio de cinco segundos. Os dois ângulos compartilham o mesmo movimento e a mesma bola. A jogada é coreografada. O jogador usa volumes articulados, poses de tornozelo e solução geométrica para os joelhos. O experimento serve para avaliar o contato e o custo gráfico em cada PC.

## Rodar

Abra project.godot no Godot 4.7.2 e pressione F5. O renderizador Compatibility usa OpenGL. A janela é de 1280 × 720. Com Q, alterne a resolução interna entre 50%, 75% e 100% em cada dimensão. A inicial é 75%. C troca a câmera. Espaço pausa e R retorna ao início. A batida ocorre em 2 s. Use C com a cena pausada para examinar a mesma pose.

O painel mede o intervalo real entre quadros e mostra o percentil 95 das últimas 240 amostras. Após mudar de escala, aguarde a janela de amostras encher. Compare o mesmo ângulo e o mesmo PC. Para avaliar fluidez a 24 fps, use 41,7 ms por quadro como referência. Versões de driver, cap de FPS e sincronização vertical afetam a medida.

## Exportar no Windows

Com Godot e FFmpeg no PATH, execute no PowerShell a partir desta pasta:

    .\exportar.ps1
    .\exportar.ps1 -Gol

Para indicar o executável explicitamente, use o binário de console do Godot:

    .\exportar.ps1 -Godot "C:\Godot\Godot_console.exe" -FFmpeg "C:\ffmpeg\bin\ffmpeg.exe"

O script grava 120 quadros em escala integral, sem painel. Cria um AVI intermediário e um MP4 H.264 com nomes únicos em renders/. O modo de filme trabalha a passo fixo para gerar os quadros mesmo quando a prévia em tempo real fica lenta. A cena é silenciosa.

## Desenvolvimento

campo.gd define o palco, a iluminação, as duas câmeras, os materiais e a coreografia. STRIKE_KEYS controla o tornozelo do chute em metros e segundos. O pé de apoio tem uma posição fixa. ball_path usa a mesma pose do contato para unir o cruzamento e a finalização.

Teste de regressão, dentro desta pasta:

    godot --headless --path . --script verificar.gd

Este módulo funciona sem serviços pagos, IA de vídeo ou SDKs proprietários. Ferramentas reutilizadas: [Godot](https://github.com/godotengine/godot) e [FFmpeg](https://github.com/FFmpeg/FFmpeg). O pacote usa as instalações locais dessas ferramentas.
