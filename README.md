# Personal Video Streamer

Simple Flask application that scans a `videos/` directory and serves a small
web interface to play them using a Video.js player. Metadata about videos is
stored in TinyDB on startup.

## Usage

1. Place your video files inside the `videos/` directory.
2. Ensure `ffmpeg` is installed so the server can read durations and generate
   thumbnails.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

5. Open your browser at `http://localhost:5000`.

The first time the server starts it will create thumbnails in the `thumbs/`
folder and store metadata in `db.json`.
