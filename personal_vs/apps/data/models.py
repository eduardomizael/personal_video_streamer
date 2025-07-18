from pathlib import Path

from django.db import models
from django.utils import timezone

from apps.base.models import BaseModel


class MediaDirectory(models.Model):
    """
    Representa um diretório local a ser escaneado em busca de vídeos.
    """
    name = models.CharField(
        max_length=255,
        help_text="Nome descritivo deste diretório (ex: 'Filmes', 'Gravações_2025', etc.)"
    )
    path = models.CharField(
        max_length=1024,
        unique=True,
        help_text="Caminho absoluto no sistema de arquivos"
    )
    recursive = models.BooleanField(
        default=True,
        help_text="Se True, busca também em subpastas"
    )

    last_scanned = models.DateTimeField(
        null=True, blank=True,
        help_text="Data/hora da última varredura"
    )

    def __str__(self):
        return f"{self.name} ({self.path})"


class Video(BaseModel):
    """
    Armazena metadados de um arquivo de vídeo encontrado num MediaDirectory.
    """
    directory = models.ForeignKey(MediaDirectory, null=True, on_delete=models.CASCADE, related_name="videos")
    file_name = models.CharField(max_length=255,
                                 help_text="Nome do arquivo, ex: 'video_exemplo.mp4'")
    hash = models.CharField(max_length=32, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True,
                             help_text="Título extraído ou definido manualmente")
    description = models.TextField(
        blank=True,
        help_text="Descrição ou anotação opcional"
    )
    path = models.CharField(max_length=256, null=True, blank=True)

    # Metadados técnicos
    duration = models.FloatField(
        default=0,
        help_text="Duração em segundos"
    )
    width = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Largura em pixels"
    )
    height = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Altura em pixels"
    )
    format = models.CharField(
        max_length=50,
        blank=True,
        help_text="Formato contêiner (mp4, mkv, avi, etc.)"
    )
    codec = models.CharField(
        max_length=50,
        blank=True,
        help_text="Codec de vídeo (h264, h265, vp9, etc.)"
    )
    size = models.BigIntegerField(
        default=0,
        help_text="Tamanho do arquivo em bytes"
    )

    # Imagem de preview gerada (thumbnail)
    thumbnail = models.ImageField(
        upload_to="media/thumbnails/",
        null=True, blank=True
    )

    # Datas de referência
    file_created = models.DateTimeField(
        help_text="Data de criação do arquivo no disco",
        default=timezone.now
    )
    scanned_at = models.DateTimeField(
        auto_now=True,
        help_text="Quando esses metadados foram atualizados"
    )

    class Meta:
        ordering = ["-scanned_at", "file_name"]

    def __str__(self):
        return self.title or self.file_name

    @property
    def file_size(self):
        return self.size / 1024 / 1024

    @property
    def file_size_human(self):
        return f"{self.file_size:.2f} MB"

    @property
    def file_path(self):
        return f"{Path(self.directory.path).absolute() / self.file_name}"
