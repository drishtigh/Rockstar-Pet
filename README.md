# Rockstar‑Pet

Generate a poster‑style “album cover” for your pet from a short quiz and 1–5 photos. The app creates a 4:5 poster with a square photo, bold title, track list, and liner notes — all laid out and rendered server‑side with Pillow.

## Features
- Poster output: 4:5 ratio image saved to `static/generated/`
- Square photo top layout with vibe‑based background color
- Fixed poster typography (Californication‑inspired), title auto‑fit to width
- Dynamic tracklist: titles and numbering auto‑fit, 1–2 columns
- Liner notes: wrapped and auto‑sized to avoid overlap, visible “LINER NOTES” label
- Photo treatments: Auto, Californication, Melodrama, Gig (applied to the photo only)
- All poster text in black; no shadows
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

## Usage
- Enter your pet’s name.
- Answer the quick quiz (energy, vibe, quirks, etc.).
- Choose a Photo Treatment (text layout is fixed):
	- Auto (picks based on vibe)
	- Californication (blue/orange tint)
	- Melodrama (deep blue + vignette)
	- Gig (high contrast + grain)
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
- Text looks too large or clipped:
	- Title and tracks auto‑fit; shorten text if you want larger sizing.
	- Very long liner notes are trimmed to fit (label remains visible).
- Fonts not applied:
	- Confirm font files in `static/fonts/` and exact names.
	- On Windows, Impact/Arial Black should be available.

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
- Additional photo treatments (B&W Minimal, Newspaper Halftone)
- Texture overlays (paper, film grain)
- More vibe‑specific fonts and micro‑icons
- Export sizes (social square, A4/Letter print)
