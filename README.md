![cover_1764343753_8033](https://github.com/user-attachments/assets/08ac0582-610f-4946-abd0-2c84fdf702ba)
#Rockstar‑Pet

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
- Interactive per‑track audio: tiny play buttons directly on the poster next to each track number (30s capped playback, uniqueness enforced)

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

## Audio Previews (12-File Pool, Optional)
The app supports per-track short (~25–35s) audio previews. It uses a fixed curated pool of 12 royalty‑free files and enforces uniqueness: no two tracks in a single poster reuse the same audio.

Place these files (MP3 preferred, WAV accepted) in `static/audio/`:

- `energy_fast.mp3` — High/zoomie energy
- `energy_chill.mp3` — Relaxed / mellow
- `regal_grand.mp3` — Majestic / stately / regal
- `goofball_quirky.mp3` — Silly / comedic / offbeat
- `adventurer_outdoor.mp3` — Explorer / outdoorsy / quest
- `mischief_sneaky.mp3` — Sneaky / playful trouble
- `vocal_opera.mp3` — Big dramatic vocal vibe
- `vocal_comic_blep.mp3` — Light, humorous blep/snort
- `cozy_loaf.mp3` — Warm, soft, loafing
- `spooky_stare.mp3` — Eerie / mysterious stare
- `playful_socks_pizz.mp3` — Plucky, toy-like, sock antics
- `neutral_default.mp3` — Neutral fallback (used only if pool exhausted or no match)

Selection logic (simplified): each generated track title produces an ordered candidate list of fitting IDs; the app picks the first still-unused audio. If all candidates are already used, it assigns an unused pool file; if the pool is fully consumed (12+ tracks), remaining tracks fall back to `neutral_default`. Result: maximum distinctness > perfect semantic matching.

Notes:
- Length beyond ~35s is fine; the front-end stops playback around 30s.
- If a mapped filename is missing, the result page shows a warning with the expected name.
- You can safely swap any file later; naming is the contract.
- Playback UI: Each track line on the poster has a circular play button placed to the left of its number. Clicking toggles play/pause. Only one track plays at a time.
- Missing audio behavior: Clicking a play button for a track without a corresponding file surfaces a warning below the poster (expected `<id>.mp3` or `.wav`).
- Customization: Adjust icon positioning or size in `templates/result.html` inside the `layoutHotspots()` function (edit the `iconSize` calculation or vertical offset). Accessibility states use `aria-pressed` on the button.

### Cleanup legacy generated audio
If you previously generated or added the older trait/variant WAV sets (`quirk_*`, `vibe_*`, `energy_zoomies*`, `mischief_heist*`, `vocal_blep*`, `default_v*`), remove them to avoid clutter. A helper script is provided:

```powershell
python .\tools\cleanup_audio.py
```

It will:
- Rename malformed double-extension files (e.g. `energy_chill.mp3.mp3` -> `energy_chill.mp3`).
- Rename `goofball_quirky.mp.mp3` -> `goofball_quirky.mp3`.
- Delete legacy WAV variants and unused stems.
- Report any curated files still missing.

### Legacy procedural generator (optional)
If you want quick placeholder tones instead of curated music, a legacy script can synthesize simple WAVs:

```powershell
python .\tools\generate_audio.py
```

Generated `.wav` files go to `static/audio/`. The app prefers `.mp3` when both exist. Convert with ffmpeg if desired:

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
