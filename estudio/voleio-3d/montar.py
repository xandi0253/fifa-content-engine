"""Monta planos em ordem, com áudio, em um MP4 de 720p ou 1080p."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def run(*args):
    subprocess.run(args, check=True)


def montar(planos, saida, altura):
    if saida.suffix.lower() != ".mp4":
        raise ValueError("Use a extensão .mp4 para a saída.")
    if saida.exists():
        raise ValueError(f"A saída já existe: {saida}")
    for plano in planos:
        if not plano.is_file():
            raise ValueError(f"Plano ausente: {plano}")
    for programa in ("ffmpeg", "ffprobe"):
        if not shutil.which(programa):
            raise ValueError(f"Instale {programa} e inclua o executável no PATH.")
    saida.parent.mkdir(parents=True, exist_ok=True)
    largura = altura * 16 // 9
    filtro = (f"fps=24,scale={largura}:{altura}:force_original_aspect_ratio=decrease:"
              f"force_divisible_by=2,pad={largura}:{altura}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p")
    with tempfile.TemporaryDirectory(dir=saida.parent) as tmp:
        pasta = Path(tmp)
        lista = []
        for i, plano in enumerate(planos):
            dados = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                             "stream=codec_type", "-of", "json", plano])
            tipos = [s["codec_type"] for s in json.loads(dados)["streams"]]
            if "video" not in tipos:
                raise ValueError(f"O plano precisa de uma faixa de vídeo: {plano}")
            entradas = ["-i", plano]
            audio = "0:a:0"
            if "audio" not in tipos:
                entradas += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
                audio = "1:a:0"
            nome = f"plano-{i:05d}.mkv"
            video = pasta / "video.mkv"
            run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", plano, "-map", "0:v:0",
                "-vf", filtro, "-an", "-c:v", "ffv1", video)
            quadros = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams",
                "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets",
                "-of", "csv=p=0", video]))
            # 48 kHz / 24 fps gives exactly 2000 audio samples per video frame.
            faixa = f"aresample=48000,apad,atrim=end_sample={quadros*2000},asetpts=N/SR/TB"
            run("ffmpeg", "-v", "error", "-nostdin", *entradas, "-i", video,
                "-map", f"{1 if audio == '0:a:0' else 2}:v:0",
                "-map", audio, "-af", faixa, "-ac", "2", "-c:v", "copy", "-c:a", "pcm_s16le",
                pasta / nome)
            lista.append(f"file '{nome}'")
        manifesto = pasta / "lista.txt"
        manifesto.write_text("\n".join(lista)+"\n", encoding="ascii")
        produto = pasta / "final.mp4"
        run("ffmpeg","-v","error","-nostdin","-f","concat","-safe","1","-i",manifesto,
            "-af","aresample=async=1:first_pts=0","-c:v","libx264","-crf","18","-preset","fast",
            "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",produto)
        # Exclusive creation also protects simultaneous runs targeting the same file.
        with produto.open("rb") as src, saida.open("xb") as dest:
            try:
                shutil.copyfileobj(src,dest)
            except BaseException:
                dest.close()
                saida.unlink(missing_ok=True)
                raise


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("planos", nargs="+", type=Path, help="Clipes na ordem do episódio")
    cli.add_argument("--saida", required=True, type=Path)
    cli.add_argument("--altura", choices=(720,1080), default=720, type=int)
    args = cli.parse_args()
    try:
        montar(args.planos, args.saida, args.altura)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        cli.exit(1, f"Falha na montagem: {exc}\n")
