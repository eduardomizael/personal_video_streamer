import hashlib
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
import random

from django.utils import timezone

from apps.data.models import MediaDirectory, Video

logger = logging.getLogger('django')

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv'}


def compute_hash(file_path, chunk_size=8192):
    """
    Calcula o hash MD5 de um arquivo para identificar mudanças.
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            md5.update(chunk)
    print(f"Hash MD5 de {file_path} calculado.")
    return md5.hexdigest()


def probe_metadata(file_path):
    """
    Obtém metadados de vídeo usando ffprobe.
    Retorna dict com duration, width, height, format, codec.
    """
    cmd = [
        'ffprobe', '-v', 'error',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(result.stdout)

    fmt = info.get('format', {})
    duration = float(fmt.get('duration', 0.0))
    container = fmt.get('format_name', '')

    # procura o primeiro stream de vídeo
    width = height = None
    codec = ''
    for stream in info.get('streams', []):
        if stream.get('codec_type') == 'video':
            width = stream.get('width')
            height = stream.get('height')
            codec = stream.get('codec_name')
            break
    print(f"Metadata de {file_path} obtida.")
    return {
        'duration': duration,
        'format': container,
        'codec': codec,
        'width': width,
        'height': height,
    }


def generate_thumbnail(file_path, thumb_dir, time_offset='00:00:01'):  # hh:mm:ss
    """
    Gera uma miniatura usando ffmpeg e retorna o caminho salvo.
    """
    os.makedirs(thumb_dir, exist_ok=True)
    base = Path(file_path).stem
    thumb_path = Path(thumb_dir) / f"{base}.jpg"
    time_offset = f"00:{str(random.randint(1, 3)).zfill(2)}:{str(random.randint(1, 59)).zfill(2)}"

    cmd = [
        'ffmpeg', '-ss', time_offset,
        '-i', file_path,
        '-vframes', '1',
        str(thumb_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Erro ao gerar thumbnail: {result.stderr}")

    print(f"Thumbnail {thumb_path} gerada.")
    return str(thumb_path)


def process_video_file(directory: MediaDirectory, file_path: str, thumb_root: str):
    """
    Cria ou atualiza a instância Video para o arquivo dado.
    """
    file_name = os.path.basename(file_path)
    file_stat = os.stat(file_path)
    file_size = file_stat.st_size
    file_ctime = timezone.make_aware(
        datetime.fromtimestamp(file_stat.st_ctime)
    )

    file_hash = compute_hash(file_path)
    meta = probe_metadata(file_path)

    # Gera thumbnail relativa a MEDIA_ROOT/thumbnails/YYYY/MM/DD/
    # thumb_dir = os.path.join(thumb_root, timezone.now().strftime('%Y/%m/%d'))
    thumb_dir = Path(thumb_root) / 'thumbnails'
    thumb_path = generate_thumbnail(file_path, thumb_dir)

    video_obj, created = Video.objects.update_or_create(
        directory = directory,
        file_name = file_name,
        defaults={
            'hash': file_hash,
            'duration': meta['duration'],
            'format': meta['format'],
            'codec': meta['codec'],
            'width': meta['width'],
            'height': meta['height'],
            'size': file_size,
            'file_created': file_ctime,
            'thumbnail': thumb_path,
        }
    )
    print(f"Video {file_name} processado.")
    return video_obj


def scan_media_directories(thumb_root: str):
    """
    Varre todos os MediaDirectory ativos e processa arquivos de vídeo.
    """
    dirs = MediaDirectory.objects.all()
    for media_dir in dirs:
        print(f'Iniciando análise no diretório {media_dir.path}...')
        root = media_dir.path
        if media_dir.recursive:
            walker = os.walk(root)
        else:
            walker = [(root, [], os.listdir(root))]

        for base, _, files in walker:
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in VIDEO_EXTENSIONS:
                    fpath = os.path.join(base, fname)
                    try:
                        process_video_file(media_dir, fpath, thumb_root)
                    except Exception as e:
                        # Aqui você pode logar erros específicos por arquivo
                        logger.error(f"Erro processando {fpath}: {e}")

        # Atualiza timestamp de varredura
        media_dir.last_scanned = timezone.now()
        media_dir.save()
        print(f'Diretório {media_dir.path} processado com sucesso.')


# Exemplo de uso dentro de um management command
# from django.core.management.base import BaseCommand
#
# class Command(BaseCommand):
#     help = 'Escaneia diretórios de mídia e popula/atualiza Videos'
#
#     def handle(self, *args, **options):
#         thumb_root = '/path/to/media/thumbnails'
#         scan_media_directories(thumb_root)
#         self.stdout.write(self.style.SUCCESS('Scan concluído.'))
