import subprocess
import hashlib
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, send_file, abort, send_from_directory
from tinydb import TinyDB, Query

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


def sync_videos() -> None:
    """Synchronize database with files on disk using hashes."""
    VIDEO_DIR.mkdir(exist_ok=True)
    THUMB_DIR.mkdir(exist_ok=True)

    existing_hashes: set[str] = set()
    allowed_ext = {".mp4", ".mkv", ".webm", ".avi"}

    for file in sorted(VIDEO_DIR.iterdir()):
        if file.suffix.lower() not in allowed_ext:
            continue
        file = file.resolve()
        file_hash = hash_file(file)
        if not file_hash:
            continue
        existing_hashes.add(file_hash)

        duration = get_video_duration(file)
        thumb = generate_thumbnail(file)
        entry = db.get(Query().hash == file_hash)

        data = {
            "hash": file_hash,
            "name": file.stem,
            "path": str(file.resolve()),
            "duration": duration,
            "thumb": thumb.name,
        }

        if entry:
            db.update(data, Query().hash == file_hash)
        else:
            db.insert(data)

    # Remove entries whose files no longer exist
    for entry in db.all():
        if entry.get("hash") not in existing_hashes or not Path(entry.get("path", "")).exists():
            db.remove(Query().hash == entry.get("hash"))


def load_videos() -> None:
    """Deprecated. Use sync_videos instead."""
    sync_videos()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/videos")
def videos():
    """Return list of videos with their database ids."""
    return jsonify([{**doc, "id": doc.doc_id} for doc in db])


@app.route("/video/<int:video_id>")
def video(video_id: int):
    """Stream the video associated with the given id."""
    entry = db.get(doc_id=video_id)
    if not entry:
        abort(404)
    return send_from_directory(entry["path"])

@app.route("/thumb/<file_hash>")
def thumb(file_hash: str):
    entry = db.get(Query().hash == file_hash)
    if not entry:
        abort(404)
    thumb_path = THUMB_DIR / entry.get("thumb", "")
    if not thumb_path.exists():
        abort(404)
    return send_file(thumb_path)


if __name__ == "__main__":
    sync_videos()
    app.run(debug=True, host="0.0.0.0", port=5000)
