param([string]$Godot="godot", [string]$FFmpeg="ffmpeg", [switch]$Gol)
$ErrorActionPreference = "Stop"
$nome = if ($Gol) { "voleio-gol" } else { "voleio-lateral" }
$pasta = Join-Path $PSScriptRoot "renders"
New-Item -ItemType Directory -Force $pasta | Out-Null
$id = [guid]::NewGuid().ToString("N").Substring(0,8)
$base = Join-Path $pasta "$nome-$id"
$opcoes = @("--path", $PSScriptRoot, "--write-movie", "$base.avi", "--fixed-fps", "24", "--quit-after", "120", "--", "--filme")
if ($Gol) { $opcoes += "--gol" }
& $Godot @opcoes
if ($LASTEXITCODE -ne 0 -or !(Test-Path "$base.avi")) { throw "Falha na gravação do Godot." }
& $FFmpeg -v error -n -i "$base.avi" -frames:v 120 -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$base.mp4"
if ($LASTEXITCODE -ne 0) { throw "Falha na conversão. A gravação AVI está em $base.avi." }
Write-Output "$base.mp4"
