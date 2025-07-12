import subprocess
from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory
from tinydb import TinyDB

VIDEO_DIR = Path("videos")
THUMB_DIR = Path("thumbs")
DB_FILE = "db.json"

app = Flask(__name__)

db = TinyDB(DB_FILE)


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
    THUMB_DIR.mkdir(exist_ok=True)
    thumb = THUMB_DIR / f"{path.stem}.jpg"
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


def load_videos() -> None:
    """Scan VIDEO_DIR and populate the database."""
    db.truncate()
    if not VIDEO_DIR.exists():
        return
    for file in sorted(VIDEO_DIR.iterdir()):
        if file.suffix.lower() not in {".mp4", ".mkv", ".webm", ".avi"}:
            continue
        duration = get_video_duration(file.absolute())
        thumb = generate_thumbnail(file.absolute())
        db.insert(
            {
                "name": file.stem,
                "path": str(file.absolute()),
                "duration": duration,
                "thumb": thumb.name,
            }
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/videos")
def videos():
    return jsonify(db.all())


@app.route("/video/<path:filename>")
def video(filename):
    return send_from_directory(VIDEO_DIR, filename)


@app.route("/thumb/<path:filename>")
def thumb(filename):
    return send_from_directory(THUMB_DIR, filename)


if __name__ == "__main__":
    load_videos()
    app.run(debug=True, host="0.0.0.0", port=5000)
