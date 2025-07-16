import hashlib
import subprocess
from pathlib import Path
from django.conf import settings
from apps.data.models import Video

ALLOWED_EXT = {".mp4", ".mkv", ".webm", ".avi"}

def get_video_duration(path: Path) -> int:
    """Return duration of video in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        duration = float(result.stdout.strip())
        return int(duration)
    except Exception as exc:  # pragma: no cover - depends on ffprobe
        print(f"Failed to get duration for {path}: {exc}")
        return 0


def generate_thumbnail(path: Path) -> Path:
    """Generate a thumbnail for the video and return its path."""
    thumb_dir = settings.THUMBNAIL_DIR
    thumb_dir.mkdir(exist_ok=True)
    thumb = thumb_dir / f"{path.stem}.jpg"
    if thumb.exists():
        return thumb
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-ss",
                "00:00:01.000",
                "-vframes",
                "1",
                str(thumb),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - depends on ffmpeg
        print(f"Failed to create thumbnail for {path}: {exc}")
    return thumb


def hash_file(path: Path) -> str:
    """Return SHA256 hash of a file."""
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except FileNotFoundError:
        return ""
    return h.hexdigest()


def update_video_data(file_path):
    if not file_path.exists():
        return

    if not file_path.suffix.lower() in ALLOWED_EXT:
        return

    video_path = file_path.resolve()
    video_hash = hash_file(video_path)
    video_title = video_path.stem
    video_thumbnail = generate_thumbnail(video_path)
    video_duration = get_video_duration(video_path)

    video = Video.objects.get_or_create(hash=video_hash)
    video.update(path=video_path, title=video_title, thumbnail=video_thumbnail, duration=video_duration)


def update_all_video_data(video_dir=None):
    video_dir = video_dir or settings.VIDEO_DIR

    for file in video_dir.glob(ALLOWED_EXT):
        update_video_data(file)
