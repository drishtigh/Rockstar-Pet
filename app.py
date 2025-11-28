from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
import os
import sys
import random
import time

# Assuming the functions from Pet_Album.py are moved here or imported
# For simplicity, I'll include the necessary functions directly in this file.

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')
GENERATED_DIR = os.path.join(STATIC_DIR, 'generated')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def _pick_text_color(bg_rgb):
    r, g, b = bg_rgb
    # perceived luminance
    luminance = 0.299*r + 0.587*g + 0.114*b
    return (0, 0, 0) if luminance > 160 else (255, 255, 255)

def _apply_vibe_filter(img, vibe, energy):
    if vibe == 'Regal':
        img = ImageEnhance.Contrast(img).enhance(1.1)
        gold = Image.new('RGBA', img.size, (212, 175, 55, 28))
        img = Image.alpha_composite(img.convert('RGBA'), gold).convert('RGB')
    elif vibe == 'Goofball':
        img = ImageEnhance.Color(img).enhance(1.3)
        img = ImageEnhance.Brightness(img).enhance(1.05)
    elif vibe == 'Adventurer':
        warm = Image.new('RGBA', img.size, (255, 140, 0, 24))
        img = Image.alpha_composite(img.convert('RGBA'), warm).convert('RGB')
        img = ImageEnhance.Contrast(img).enhance(1.05)
    elif vibe == 'Snuggler':
        img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
        pastel = Image.new('RGBA', img.size, (255, 192, 203, 20))
        img = Image.alpha_composite(img.convert('RGBA'), pastel).convert('RGB')
    elif vibe == 'Bossy':
        img = ImageEnhance.Contrast(img).enhance(1.25)
        img = ImageEnhance.Sharpness(img).enhance(1.1)
    elif vibe == 'Wise Sage':
        gray = ImageOps.grayscale(img)
        img = ImageOps.colorize(gray, black="#3b2f2f", white="#f5e6c8")
    # Energy tweaks
    if energy == 'Zoomies Every Hour':
        img = ImageEnhance.Contrast(img).enhance(1.05)
    elif energy == 'Chill':
        img = ImageEnhance.Color(img).enhance(0.95)
    return img

def _windows_fonts_dir():
    # Common Windows fonts directory
    win_dir = os.environ.get('WINDIR', r'C:\\Windows')
    return os.path.join(win_dir, 'Fonts')

def _resolve_font_path(candidates):
    # Search in static/fonts first, then Windows fonts
    search_dirs = [os.path.join(STATIC_DIR, 'fonts'), _windows_fonts_dir()]
    for d in search_dirs:
        for name in candidates:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None

def _load_font(candidates, size):
    path = _resolve_font_path(candidates)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    # fallback
    try:
        return ImageFont.truetype('arial.ttf', size)
    except Exception:
        return ImageFont.load_default()

def _fonts_for_vibe(vibe, title_size, artist_size):
    # Map vibe to likely font files (Windows names)
    vibe_map = {
        'Regal': (['georgia.ttf', 'times.ttf', 'timesbd.ttf', 'cambria.ttc'], ['georgiaz.ttf', 'georgia.ttf', 'times.ttf']),
        'Goofball': (['comic.ttf', 'comicbd.ttf', 'arial.ttf'], ['comic.ttf', 'arial.ttf']),
        'Adventurer': (['rock.ttf', 'rockb.ttf', 'segoeuib.ttf', 'impact.ttf'], ['segoeui.ttf', 'arialbd.ttf']),
        'Snuggler': (['segoeui.ttf', 'calibri.ttf', 'verdana.ttf'], ['segoeui.ttf', 'calibri.ttf']),
        'Bossy': (['impact.ttf', 'arialbd.ttf', 'arialblack.ttf'], ['arialbd.ttf', 'impact.ttf']),
        'Wise Sage': (['cour.ttf', 'georgia.ttf', 'times.ttf'], ['cour.ttf', 'georgia.ttf'])
    }
    title_candidates, artist_candidates = vibe_map.get(vibe, (['arial.ttf'], ['arial.ttf']))
    return _load_font(title_candidates, title_size), _load_font(artist_candidates, artist_size)

def _draw_text_with_spacing(draw, position, text, font, fill, spacing=0, stroke_width=0, stroke_fill=None):
    if spacing <= 0:
        draw.text(position, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        return
    x, y = position
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        w, h = draw.textbbox((0, 0), ch, font=font)[2:]
        x += w + spacing

def generate_cover_image(pet_info, photo_path=None, out_dir=GENERATED_DIR, size=1024):
    # Load image or fallback solid background
    if photo_path and os.path.exists(photo_path):
        img = Image.open(photo_path).convert('RGB')
    else:
        # fallback solid
        img = Image.new('RGB', (size, size), (50, 70, 100))

    # Crop to square focus center
    img = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    # Apply vibe filter
    vibe = pet_info.get('vibe')
    energy = pet_info.get('energy')
    img = _apply_vibe_filter(img, vibe, energy)

    # Create drawing context
    draw = ImageDraw.Draw(img)

    # Extract a rough dominant color by downsampling
    small = img.resize((50, 50))
    pal = small.quantize(colors=5, method=Image.MEDIANCUT)
    palette_img = pal.convert('RGB')
    colors = palette_img.getcolors(50*50)
    colors = sorted(colors, key=lambda c: c[0], reverse=True)
    main_color = colors[0][1] if colors else (230, 230, 230)
    text_color = _pick_text_color(main_color)

    # Titles
    title = pet_info.get('album_title', 'Greatest Hits')
    artist = pet_info.get('artist_name', 'The Artist')

    # Font selection per vibe
    font_title, font_artist = _fonts_for_vibe(vibe, title_size=64, artist_size=36)

    # Energy affects casing and spacing/tilt
    spacing = 0
    title_draw = title
    if energy == 'Zoomies Every Hour':
        title_draw = title.upper()
    elif energy == 'Chill':
        title_draw = title.title()
        spacing = 2

    # Render title on its own layer if tilt is needed
    needs_tilt = (energy == 'Zoomies Every Hour')
    shadow = (0, 0, 0)
    stroke_w = 2
    stroke_c = shadow

    if needs_tilt:
        # Create transparent layer
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        tw, th = layer_draw.textbbox((0, 0), title_draw, font=font_title)[2:]
        tx = (size - tw) // 2
        ty = int(size * 0.07)
        _draw_text_with_spacing(layer_draw, (tx+2, ty+2), title_draw, font_title, shadow, spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)
        _draw_text_with_spacing(layer_draw, (tx, ty), title_draw, font_title, text_color, spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)
        layer = layer.rotate(-4, resample=Image.Resampling.BICUBIC, center=(size//2, int(size*0.15)), expand=False)
        img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
        draw = ImageDraw.Draw(img)
    else:
        tw, th = draw.textbbox((0, 0), title_draw, font=font_title)[2:]
        tx = (size - tw) // 2
        ty = int(size * 0.07)
        _draw_text_with_spacing(draw, (tx+2, ty+2), title_draw, font_title, shadow, spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)
        _draw_text_with_spacing(draw, (tx, ty), title_draw, font_title, text_color, spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)

    # Artist position (bottom center)
    aw, ah = draw.textbbox((0, 0), artist, font=font_artist)[2:]
    ax = (size - aw) // 2
    ay = int(size * 0.86)
    draw.text((ax+1, ay+1), artist, font=font_artist, fill=shadow, stroke_width=1, stroke_fill=shadow)
    draw.text((ax, ay), artist, font=font_artist, fill=text_color, stroke_width=1, stroke_fill=shadow)

    # Optional stickers based on traits (minimal, simple icons)
    stickers = []
    if pet_info.get('vocalness_description') == 'Opera' or pet_info.get('sneakiness') == 'Master thief':
        stickers.append('Deluxe')
    if pet_info.get('wingman_activity') == 'Park meetups':
        stickers.append('Live at the Park')
    if pet_info.get('wingman_activity') in ('People-watching', 'Bird TV'):
        stickers.append('Window Sessions')

    sx, sy = int(size*0.05), int(size*0.85)
    for s in stickers[:2]:
        # Draw rounded sticker
        pad = 8
        sw, sh = draw.textbbox((0, 0), s, font=font_artist)[2:]
        box = [sx-6, sy-6, sx+sw+pad, sy+sh+pad]
        draw.rectangle(box, fill=(255, 255, 255, 180), outline=(0,0,0))
        draw.text((sx, sy), s, font=font_artist, fill=(0, 0, 0))
        sy -= sh + 18

    # Save
    filename = f"cover_{int(time.time())}_{random.randint(1000,9999)}.jpg"
    out_path = os.path.join(out_dir, filename)
    img.save(out_path, quality=90)
    return filename

def generate_album_content(pet_info):
    """Generates the album content based on the pet's info using a detailed mapping plan."""

    track_list = []
    easter_eggs = []
    
    # --- Global Rules ---
    energy = pet_info.get('energy')
    if energy == 'Chill':
        track_count = 6
    elif energy == 'Balanced':
        track_count = 7
    else: # Zoomies Every Hour
        track_count = 8

    # --- Per-question Mappings & Title Templates ---
    
    # Vibe sets the theme
    vibe = pet_info.get('vibe')
    vibe_map = {
        'Regal': ("Throne Room Overture", "Royal Snack Intermezzo", "Crown and Whiskers"),
        'Goofball': ("Sock Jokes, Pt. II", "Katamari of Chaos", "Boop Symphony"),
        'Adventurer': ("Trail Mix", "Backyard Odyssey", "Map of Smells"),
        'Snuggler': ("Velcro Heart", "Blanket Crescendo", "Chest Purr Ballad"),
        'Bossy': ("Command Performance", "Rules of the House (Remix)", "Schedule Keeper"),
        'Wise Sage': ("Ancient Sunbeam", "Oracle of the Couch", "Whisker Wisdom")
    }
    opener_track = random.choice(vibe_map.get(vibe, ["Pet Anthem"]))

    # Energy
    energy_map = {
        'Chill': ("Sunbeam Suite", "Pillow Fort Lullaby", "Slow Tails"),
        'Balanced': ("Afternoon Zoom", "Gentle Pounce", "Window Patrol"),
        'Zoomies Every Hour': ("Midnight Zoomies", "Carpet Sprint", "Turbo Paw")
    }
    energy_track = random.choice(energy_map.get(energy, ["Energy Flow"]))

    # Play/Hobby
    activity = pet_info.get('favorite_activity')
    activity_map = {
        'Chasing': ("Catch Me If You Can", "Shadow Sprint"),
        'Fetch': ("Bring It Back", "Tennis Ball Suite"),
        'Puzzle toys': ("Treat Riddle", "Puzzle Box Blues"),
        'Sunbathing': ("Solar Nap", "Golden Window"),
        'Bird TV': ("Feather Channel", "Window Gazette"),
        'Box forts': ("Cardboard Citadel", "Corrugated Dreams")
    }
    hobby_track = random.choice(activity_map.get(activity, ["Playtime"]))

    # Quirk/Signature Move
    move = pet_info.get('signature_move')
    move_map = {
        'Head tilt': ("Tilted Questions", "Curious Overture"),
        'Side-eye': ("The Look", "Sidelong Sonata"),
        'Zoomies': ("Hallway Rally", "Spin Cycle"),
        'Slow blink': ("Blink Twice", "Patience Prelude"),
        'Spooky stare': ("Midnight Stare", "Ghost Lamp"),
        'Bread loaf': ("Loaf Mode", "Yeasty Rest")
    }
    quirk_track = random.choice(move_map.get(move, ["Signature Move"]))

    # Communication/Favorite Sound
    sound = pet_info.get('favorite_sound')
    sound_map = {
        'Purr/soft chirps': ("Purr Engine", "Chirp Suite"),
        'Barks/meows': ("Woof Anthem", "Meow March"),
        'Snorts/bleps': ("Blep Etude", "Snort Groove"),
        'Dramatic sighs': ("Sigh Sonata", "Long Exhale")
    }
    sound_track = random.choice(sound_map.get(sound, ["Pet Sounds"]))

    # Affection/Cuddle Ballad
    cuddle = pet_info.get('cuddle_factor')
    cuddle_map = {
        'Only when I decide': ("By Appointment Only", "Selective Snuggles"),
        'Sometimes': ("Occasional Warmth", "Half-Blanket Waltz"),
        'Velcro': ("Stuck Like Fur", "Velcro Ballad")
    }
    affection_track = random.choice(cuddle_map.get(cuddle, ["Cuddle Song"]))

    # Finale/Anthem
    sneakiness = pet_info.get('sneakiness')
    sneakiness_map = {
        'Law-abiding': ("Good Citizen", "Treat Tax"),
        'Occasional heist': ("Minor Caper", "Sneak Peek"),
        'Master thief': ("Grand Heist", "Midnight Mission")
    }
    finale_track = random.choice(sneakiness_map.get(sneakiness, ["Finale"]))

    # --- Assembly Logic ---
    track_list.append(f"1. {opener_track}")
    track_list.append(f"2. {energy_track}")
    
    mid_tracks = [hobby_track, quirk_track, sound_track]
    random.shuffle(mid_tracks)
    
    track_number = 3
    for track in mid_tracks:
        track_list.append(f"{track_number}. {track}")
        track_number += 1

    # Insert Skit/Interlude for Goofball or Opera
    has_interlude = False
    if vibe == 'Goofball':
        habit = pet_info.get('weirdest_habit')
        if habit == 'Vocal monologues':
             track_list.insert(random.randint(2, 4), f"{track_number}. Soliloquy at Dusk (Skit)")
        else:
             track_list.insert(random.randint(2, 4), f"{track_number}. Goofball Interlude (Remix)")
        has_interlude = True
        track_number += 1

    if pet_info.get('vocalness_description') == 'Opera' and not has_interlude:
        track_list.insert(random.randint(2, 4), f"{track_number}. Vocal Solo (Interlude)")
        has_interlude = True
        track_number += 1

    # Add remaining tracks
    track_list.append(f"{len(track_list) + 1}. {affection_track}")
    track_list.append(f"{len(track_list) + 1}. {finale_track}")

    # Ensure track count matches energy level by adding/removing generic tracks if needed
    while len(track_list) < track_count:
        track_list.insert(-2, f"{len(track_list)}. Bonus Track")
    while len(track_list) > track_count:
        track_list.pop(random.randint(2, len(track_list) - 3))

    # Renumber tracks after all adjustments
    final_numbered_tracks = []
    for i, track in enumerate(track_list):
        title = track.split('. ', 1)[1]
        final_numbered_tracks.append(f"{i + 1}. {title}")
    
    # --- Easter Eggs ---
    if sneakiness == 'Master thief':
        easter_eggs.append("Hidden Bonus: The Heist (Secret Track)")

    return {"track_list": final_numbered_tracks, "easter_eggs": easter_eggs}

def generate_artist_name(pet_info):
    """Generates a creative artist name based on the pet's personality."""
    name = pet_info.get('artist_name', 'The Artist')
    
    vibe_map = {
        'Regal': ['Sir', 'Lady', 'Prince', 'Queen'],
        'Goofball': ['DJ', 'Lil', 'MC'],
        'Adventurer': ['Ranger', 'Scout', 'Captain', 'Voyager'],
        'Snuggler': ['Cozy', 'Velvet', 'Pillow'],
        'Bossy': ['Chief', 'Boss', 'Director', 'Commander'],
        'Wise Sage': ['Professor', 'Oracle', 'Monk', 'Sage']
    }
    
    activity_map = {
        'Fetch': "Tennis Ball Society", 'Box forts': "Box Fort Brigade",
        'Bird TV': "Birdwatchers Union", 'Sunbathing': "Sunbeam Syndicate",
        'Chasing': "Shadow Chasers", 'Puzzle toys': "Puzzle Club"
    }

    move_epithets = {
        'Side-eye': "of the Side-Eye", 'Stealing socks': "the Sock Thief",
        'Bread loaf': "the Loaf Lord", 'Zoomies': "the Zoomies General"
    }

    vocal_map = {
        'Silent film star': "Quartet", 'Chatty': "& Friends", 'Opera': "and the Howl Ensemble"
    }

    # Get attributes
    vibe = pet_info.get('vibe')
    social = pet_info.get('social')
    vocalness = pet_info.get('vocalness_description')
    sneakiness = pet_info.get('sneakiness')
    move = pet_info.get('signature_move')
    activity = pet_info.get('favorite_activity')

    # Generate potential names
    possible_names = []
    
    # Template 1: [Honorific] [Name]
    if vibe in vibe_map:
        honorific = random.choice(vibe_map[vibe])
        possible_names.append(f"{honorific} {name}")

    # Template 2: [Name] the [Epithet]
    if move in move_epithets:
        possible_names.append(f"{name} {move_epithets[move]}")

    # Template 3: [Name] & The [Band Noun]
    if social == 'Selective' and activity in activity_map:
        possible_names.append(f"{name} & The {activity_map[activity]}")
    elif social == 'Party animal' and activity in activity_map:
        possible_names.append(f"{name} and the {activity_map[activity]}")

    # Template 4: The [Collective Noun]
    if social == 'Party animal':
        possible_names.append(f"The {name} Parade")

    # Template 5: Sneaky names
    if sneakiness == 'Master thief':
        possible_names.append(f"{name} the Phantom")
    elif sneakiness == 'Occasional heist':
        possible_names.append(f"Midnight {name}")

    # Template 6: Vocalness flavor
    if vocalness in vocal_map and social != 'Shy':
        possible_names.append(f"{name} {vocal_map[vocalness]}")

    if not possible_names:
        return name # Default to just the name if no rules match

    return random.choice(possible_names)

def generate_album_title(pet_info):
    """Generates a creative album title based on the pet's personality."""
    
    energy_map = {
        'Chill': ["Loaf Mode", "Moonlit Ballads", "Slow Tails"],
        'Balanced': ["Gentle Pounce", "Afternoon Adventures"],
        'Zoomies Every Hour': ["Turbo Paw", "Midnight Zoomies", "Carpet Sprint"]
    }
    vibe_map = {
        'Regal': "Royal", 'Goofball': "Chaos", 'Adventurer': "Odyssey",
        'Snuggler': "Cozy", 'Bossy': "Command", 'Wise Sage': "Wisdom"
    }
    quirk_map = {
        'Side-eye': "Side-Eye Serenades", 'Bread loaf': "Loaf Mode (Deluxe)",
        'Stealing socks': "The Sock Heist", 'Vocal monologues': "Aria of Snacks"
    }
    sneakiness_map = {
        'Master thief': "The Heist Tapes", 'Law-abiding': "Good Citizen Songs"
    }

    # Get attributes
    energy = pet_info.get('energy')
    vibe = pet_info.get('vibe')
    quirk = pet_info.get('weirdest_habit') or pet_info.get('signature_move')
    sneakiness = pet_info.get('sneakiness')

    possible_titles = []

    # Template 1: [Vibe Adjective] [Energy Word]
    if vibe in vibe_map and energy in energy_map:
        possible_titles.append(f"{vibe_map[vibe]} {random.choice(energy_map[energy])}")

    # Template 2: [Story from Quirk]
    if quirk in quirk_map:
        possible_titles.append(f"{quirk_map[quirk]}")

    # Template 3: The [Sneakiness] Tapes
    if sneakiness in sneakiness_map:
        possible_titles.append(sneakiness_map[sneakiness])
        
    # Fallback
    if energy in energy_map:
        possible_titles.append(random.choice(energy_map[energy]))

    if not possible_titles:
        return "Greatest Hits"

    return random.choice(possible_titles)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    pet_info = request.form.to_dict()
    # Handle uploaded photos
    uploaded_files = request.files.getlist('photos') if 'photos' in request.files else []
    saved_path = None
    for file in uploaded_files:
        if not file or file.filename == '':
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        safe_name = secure_filename(file.filename)
        saved_path = os.path.join(UPLOAD_DIR, f"{int(time.time())}_{random.randint(100,999)}_{safe_name}")
        file.save(saved_path)
        break
    
    # Set mischief and vocalness scores based on descriptions
    if pet_info.get('sneakiness') == 'Master thief': pet_info['mischief'] = 5
    elif pet_info.get('sneakiness') == 'Occasional heist': pet_info['mischief'] = 3
    else: pet_info['mischief'] = 1

    if pet_info.get('vocalness_description') == 'Opera': pet_info['vocalness'] = 5
    elif pet_info.get('vocalness_description') == 'Chatty': pet_info['vocalness'] = 3
    else: pet_info['vocalness'] = 1

    # Generate creative names and titles
    pet_info['artist_name'] = generate_artist_name(pet_info)
    pet_info['album_title'] = generate_album_title(pet_info)

    content = generate_album_content(pet_info)

    # Generate cover image (uses first uploaded or fallback)
    cover_filename = generate_cover_image(pet_info, saved_path)
    cover_url = url_for('static', filename=f'generated/{cover_filename}')
    
    return render_template('result.html', pet_info=pet_info, content=content, cover_url=cover_url)

if __name__ == '__main__':
    app.run(debug=True)
