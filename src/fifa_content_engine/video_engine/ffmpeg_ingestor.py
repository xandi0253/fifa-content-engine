"""Implementação concreta do VideoIngestor usando ffmpeg/ffprobe via subprocess."""

from __future__ import annotations

from pathlib import Path

from . import ffprobe, scene_detection
from .conversion import normalize
from .ingestion import VideoIngestor, VideoSource

# Formatos de container aceitos na entrada do pipeline.
SUPPORTED_INPUT_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".ts"}


class FfmpegVideoIngestor(VideoIngestor):
    """Ingestor que usa os binários ffmpeg/ffprobe do sistema.

    Fluxo:
      1. validate(): confere extensão suportada e usa ffprobe para
         garantir que o arquivo tem ao menos um stream de vídeo legível.
      2. prepare(): converte/normaliza o vídeo para mp4/h264/aac e roda
         a detecção de cenas, retornando um VideoSource enriquecido.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def validate(self, source: VideoSource) -> bool:
        if source.path.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
            return False

        if not source.path.exists():
            return False

        try:
            result = ffprobe.probe(source.path)
        except Exception:
            return False

        return result.has_video_stream

    def prepare(self, source: VideoSource) -> VideoSource:
        probe_result = ffprobe.probe(source.path)
        normalized_path = normalize(source.path, self.output_dir)
        scene_timestamps = scene_detection.detect_scenes(normalized_path)

        return VideoSource(
            path=normalized_path,
            duration_seconds=probe_result.duration_seconds,
            format_name=probe_result.format_name,
            video_codec=probe_result.video_codec,
            scene_timestamps=tuple(scene_timestamps),
        )
