# Rockstar‑Pet

Generate a poster‑style “album cover” for your pet from a short quiz and 1–5 photos. The app creates a 4:5 poster with a square photo, bold title, vertical artist on both sides, and a dynamic track list — all rendered server‑side with Pillow.

## Features
- Poster output: 4:5 ratio image saved to `static/generated/`
- Square photo top layout with background color derived from photo palette
- Fixed poster typography (Californication‑inspired), title auto‑fit inside a reserved band with stroke and anti‑clipping
- Dynamic tracklist: titles and numbering auto‑fit, 1–2 columns
- Vertical artist on both left and right edges (consistent Bahnschrift), stacked fallback for extreme length
- Single photo treatment: Melodrama (deep blue + vignette) applied to the photo only
- Palette‑driven text colors for strong visual cohesion
- Safe Windows font fallbacks plus optional bundled fonts

## Tech Stack
- Python, Flask
- Pillow (PIL) for compositing, filters, and typography
- HTML (Jinja templates), CSS, and vanilla JS (multi‑step form)

## Requirements
- Python 3.10+
- pip

Install dependencies:
```powershell
pip install flask pillow
```

Or use a virtual environment and optional requirements file:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```powershell
$env:FLASK_APP = "app.py"
python -m flask run
```
Open http://127.0.0.1:5000 in your browser.

## 30s Audio Preview (Optional)
Add short (~30s) MP3 previews that match your pet's quiz answers. Place files in `static/audio/` with these names:

- `quirk_breadloaf.mp3` — Quirk: Bread loaf
- `quirk_spooky.mp3` — Quirk: Spooky stare
- `quirk_socks.mp3` — Quirk: Stealing socks
- `mischief_heist.mp3` — Mischief: Master thief
- `vocal_opera.mp3` — Vocalness: Opera
- `vocal_blep.mp3` — Favorite sound: Snorts/bleps
- `energy_zoomies.mp3` — Energy: Zoomies Every Hour
- `energy_chill.mp3` — Energy: Chill
- `vibe_regal.mp3` — Vibe: Regal
- `vibe_goofball.mp3` — Vibe: Goofball
- `vibe_adventurer.mp3` — Vibe: Adventurer
- `default.mp3` — Fallback when no trait matches

Priority mapping (first match wins):
1. Quirk (signature move or weirdest habit)
2. Mischief (e.g., Master thief)
3. Vocalness (Opera) or Favorite sound (Snorts/bleps)
4. Energy (Zoomies/Chill) or Vibe (Regal/Goofball/Adventurer)
5. Default

Notes:
- Files longer than 30s are auto-stopped at ~30s in the player.
- If a selected file is missing, the result page shows which filename to add.

### Generate placeholder audio (no external tools)
You can generate simple 30s WAV placeholders via a pure-Python script:

```powershell
python .\tools\generate_audio.py
```

This creates `.wav` files in `static/audio/`. The app prefers `.mp3` if present, but will use `.wav` if that’s what you have. To convert WAV → MP3 (optional), use ffmpeg:

```powershell
ffmpeg -y -i input.wav -codec:a libmp3lame -qscale:a 4 output.mp3
```

## Usage
- Enter your pet’s name.
- Answer the quick quiz (energy, vibe, quirks, etc.).
- No Photo Treatment choice (text layout is fixed): the app uses Melodrama automatically (deep blue + vignette)
- Upload 1–5 photos (the first is used for the poster).
- Click Generate — you’ll see the poster and can download it.

## Output
- Posters are saved as `.jpg` files under:
```
static/generated/
```

## Project Structure
```
app.py                   # Flask app and poster generator
templates/
	index.html             # Multi‑step form UI
	result.html            # Poster display + download
static/
	style.css              # Basic styles
	uploads/               # Uploaded photos (first is used)
	generated/             # Output posters
	fonts/                 # Optional bundled fonts (e.g., Poppins)
README.md
requirements.txt (optional)
```

## Fonts
- Title: prefers Impact (built into Windows). Fallbacks: Arial Black, Arial Bold, Bahnschrift, Segoe UI Bold.
- Artist: locked to Bahnschrift for both rotated and stacked vertical modes for consistency.
- Optional: Use Poppins Black by placing files in `static/fonts/` (picked up automatically if Impact isn’t found):
```
static/fonts/Poppins-Black.ttf
static/fonts/Poppins-ExtraBold.ttf
```

## Configuration
- No environment configuration is required for basic usage.
- Fonts: add `.ttf`/`.otf` files to `static/fonts/` to override defaults.
- Allowed image types: `.jpg`, `.jpeg`, `.png`, `.webp`.

## Troubleshooting
- Poster not showing:
	- Check that `static/generated/` exists and is writable.
	- Verify the uploaded file type.
	- Ensure Flask and Pillow are installed.
- Title or artist clipping:
	- Title rendering includes padding and edge‑scan expansion. If clipping persists, try shorter text.
	- Artist name is limited to 3 words and uses Bahnschrift; extremely long names use stacked fallback.
- Fonts not applied:
	- Confirm font files in `static/fonts/` and exact names.
	- On Windows, Impact/Bahnschrift should be available.

## Development
```powershell
# Start server
$env:FLASK_APP = "app.py"; python -m flask run

# Install deps
pip install -r requirements.txt

# Freeze deps (optional)
pip freeze > requirements.txt
```

## Roadmap
- Optional manual overrides for artist name and album title
- Export title layer as transparent PNG
- Smarter palette sampling to avoid oversaturation
- Export sizes (social square, A4/Letter print)
