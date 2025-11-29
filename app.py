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
AUDIO_DIR = os.path.join(STATIC_DIR, 'audio')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

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

def _dominant_color(img, k=5):
    # Analyze dominant color of the image using adaptive palette
    small = img.copy().resize((120, 120), Image.Resampling.BILINEAR)
    pal = small.convert('P', palette=Image.Palette.ADAPTIVE, colors=max(2, k))
    pal = pal.convert('RGB')
    colors = pal.getcolors(120*120) or []
    # Sort by frequency desc
    colors.sort(key=lambda c: c[0], reverse=True)
    # Filter out too dark/too light extremes
    def lum(rgb):
        r,g,b = rgb
        return 0.299*r + 0.587*g + 0.114*b
    for count, rgb in colors:
        L = lum(rgb)
        if 30 < L < 230:
            return rgb
    # Fallback to a soft cream
    return (245, 240, 225)

def _lighten_for_background(rgb, min_luma=210):
    r, g, b = rgb
    def lum(rr, gg, bb):
        return 0.299*rr + 0.587*gg + 0.114*bb
    # Blend with white until luminance is sufficient
    mix = 0.0
    wr, wg, wb = 255, 255, 255
    rr, gg, bb = r, g, b
    for _ in range(10):
        if lum(rr, gg, bb) >= min_luma:
            break
        mix = min(1.0, mix + 0.15)
        rr = int(r*(1-mix) + wr*mix)
        gg = int(g*(1-mix) + wg*mix)
        bb = int(b*(1-mix) + wb*mix)
    return (rr, gg, bb)

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

def generate_cover_image(pet_info, photo_path=None, tracks=None, out_dir=GENERATED_DIR, size=1024):
    # Load image or fallback solid background
    if photo_path and os.path.exists(photo_path):
        img = Image.open(photo_path).convert('RGB')
    else:
        # fallback solid
        img = Image.new('RGB', (size, size), (50, 70, 100))
    # keep a copy of the original photo for square placement later
    src = img.copy()

    # Poster is always on; style controls photo treatment only
    poster_mode = True
    # Force single photo effect: melodrama only
    poster_style = 'melodrama'

    # Poster 4:5 aspect
    if poster_mode:
        width, height = size, int(size * 1.25)
    else:
        width, height = size, size

    # Apply vibe and style to the photo only; background will be derived from photo palette
    vibe = pet_info.get('vibe')
    energy = pet_info.get('energy')
    # Background will be set later after analyzing photo colors

    # Square photo placement
    photo_side = int(width * 0.78)
    px = (width - photo_side) // 2
    py = int(height * 0.07)
    photo = ImageOps.fit(src, (photo_side, photo_side), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    photo = _apply_vibe_filter(photo, vibe, energy)

    # Poster preset overlays
    def apply_vignette(im, strength=0.5):
        w, h = im.size
        vignette = Image.new('L', (w, h), 0)
        draw_v = ImageDraw.Draw(vignette)
        draw_v.ellipse((int(-0.1*w), int(-0.2*h), int(1.1*w), int(1.2*h)), fill=int(255*strength))
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=int(min(w, h)*0.08)))
        return Image.composite(Image.new('RGB', (w, h), (0, 0, 0)), im, ImageOps.invert(vignette)).convert('RGB')

    def apply_grain(im, opacity=24):
        w, h = im.size
        noise = Image.effect_noise((w, h), 8).convert('L')
        noise_rgb = Image.merge('RGB', (noise, noise, noise))
        return Image.blend(im, noise_rgb, opacity/255.0)

    # Use only melodrama photo treatment
    chosen_style = 'melodrama'

    if poster_mode:
        if chosen_style == 'californication':
            # Subtle blue/orange split tint on the photo
            w, h = photo.size
            grad = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(grad)
            for y in range(h):
                t = y / h
                r = int(255 * (1-t) * 0.2 + 255 * t * 0.8)
                b = int(255 * (1-t) * 0.8 + 255 * t * 0.2)
                gdraw.line([(0, y), (w, y)], fill=(r, 100, b, 30))
            photo = Image.alpha_composite(photo.convert('RGBA'), grad).convert('RGB')
        elif chosen_style == 'melodrama':
            # Deep blue tint and soft vignette
            blue = Image.new('RGBA', photo.size, (20, 40, 120, 40))
            photo = Image.alpha_composite(photo.convert('RGBA'), blue).convert('RGB')
            photo = apply_vignette(photo, strength=0.55)
        elif chosen_style == 'gig':
            # High contrast and grain
            photo = ImageEnhance.Contrast(photo).enhance(1.25)
            photo = ImageEnhance.Color(photo).enhance(1.1)
            photo = apply_grain(photo, opacity=18)

    # Defer pasting photo until we position title and create poster

    # Create poster background based on photo palette
    dom = _dominant_color(photo)
    bg_color = _lighten_for_background(dom)

    def _darken_for_text(rgb, max_luma=150):
        r, g, b = rgb
        def lum(rr, gg, bb):
            return 0.299*rr + 0.587*gg + 0.114*bb
        # Darken towards black until sufficiently dark for contrast
        for _ in range(8):
            if lum(r, g, b) <= max_luma:
                break
            r = int(r * 0.85)
            g = int(g * 0.85)
            b = int(b * 0.85)
        return (r, g, b)

    title_color = dom
    text_color = _darken_for_text(dom)
    poster = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(poster)
    cream = (245, 240, 225)

    # Titles
    title = pet_info.get('album_title', 'Greatest Hits')
    artist = pet_info.get('artist_name', 'The Artist')

    # Special typography for Californication poster style
    # Text layout is always Californication-style typography
    cali_typo = True
    if cali_typo:
        # Uppercase artist and album for a clean poster hierarchy
        artist_u = (artist or 'The Artist').upper()
        title_u = (title or 'Greatest Hits').upper()

        # Layout metrics (align text to photo margins)
        margin_x = px
        margin_top = int(height * 0.045)
        spacing_head = 2
        spacing_body = 1
        # Fixed photo anchor: keep photo in a stable vertical position regardless of title length
        photo_top_y = int(height * 0.14)
        # Reserve vertical band for title between margin_top and photo_top_y
        title_band_top = margin_top
        title_band_bottom = photo_top_y
        title_band_height = max(1, title_band_bottom - title_band_top)
        title_box_w = width - 2*margin_x

        def _measure_spaced_width(text, font, spacing):
            td = ImageDraw.Draw(Image.new('RGB', (1,1)))
            total = 0
            for i, ch in enumerate(text):
                ch_w = td.textbbox((0,0), ch, font=font)[2]
                total += ch_w
                if i != len(text)-1:
                    total += spacing
            return max(total, 1)

        # Fit heading font to available width AND height of the reserved title band
        def fit_font_band(candidates, text, box_w, band_h, spacing_px, start_size, min_size):
            size = start_size
            while size >= min_size:
                f = _load_font(candidates, size)
                tw = _measure_spaced_width(text, f, spacing_px)
                try:
                    ascent, descent = f.getmetrics()
                except Exception:
                    ascent, descent = f.size, int(f.size * 0.25)
                fudge = int(f.size * 0.35)
                th = ascent + descent + fudge
                if tw <= box_w and th <= band_h:
                    return f
                size -= 1
            return _load_font(candidates, min_size)

        heading_font = fit_font_band(
            [
                'impact.ttf', 'ariblk.ttf', 'arialbd.ttf',
                'bahnschrift.ttf', 'segoeuib.ttf',
                'Poppins-Black.ttf', 'Poppins-Black.otf',
                'Poppins-ExtraBold.ttf', 'Poppins-ExtraBold.otf'
            ],
            title_u,
            box_w=title_box_w,
            band_h=title_band_height,
            spacing_px=spacing_head,
            start_size=int(width*0.16),
            min_size=int(width*0.04)
        )
        sub_font = _load_font(['bahnschrift.ttf', 'arialbd.ttf', 'segoeui.ttf'], int(width * 0.045))

        # Album title occupies the band; bottom-align to touch the photo
        ty = title_band_bottom  # we will subtract title image height later for bottom alignment
        # Measure width with custom letter spacing
        tw = _measure_spaced_width(title_u, heading_font, spacing_head)
        # Compute text metrics and add generous descent padding to prevent cut-off
        # Use a direct bounding box height for reliability with multi-word titles
        bbox_full = draw.textbbox((0,0), title_u, font=heading_font)
        raw_h = bbox_full[3] - bbox_full[1]
        # Padding accounts for stroke, potential overshoot glyphs, and spacing artifacts
        stroke_w = max(1, heading_font.size // 16)
        pad_extra = int(heading_font.size * 0.28) + stroke_w * 2
        th = max(1, raw_h + pad_extra)
        # Outline settings: contrasting color and safe padding to avoid clipping
        def _lum(c):
            r,g,b = c
            return 0.299*r + 0.587*g + 0.114*b
        outline_color = (0,0,0) if _lum(title_color) > 150 else (255,255,255)
        stroke_w = max(1, heading_font.size // 16)
        pad_outline = stroke_w + heading_font.size//12 + 4
        title_img = Image.new('RGBA', (tw + pad_outline*2, th + pad_outline*2), (0,0,0,0))
        tdraw = ImageDraw.Draw(title_img)
        _draw_text_with_spacing(
            tdraw,
            (pad_outline, pad_outline),
            title_u,
            heading_font,
            title_color,
            spacing=spacing_head,
            stroke_width=stroke_w,
            stroke_fill=outline_color
        )
        # Post-render padding expansion if any stroke touches edges (edge scan to avoid clipping)
        edge_bbox = title_img.getbbox()
        if edge_bbox:
            left, top, right, bottom = edge_bbox
            needs_expand = left <= 1 or top <= 1 or right >= title_img.size[0]-2 or bottom >= title_img.size[1]-2
            if needs_expand:
                extra = max(6, heading_font.size//10 + 4)
                expanded = Image.new('RGBA', (title_img.size[0] + extra*2, title_img.size[1] + extra*2), (0,0,0,0))
                expanded.paste(title_img, (extra, extra))
                title_img = expanded
        # Post-render scaling (same idea as vertical artist scaling) to ensure title fits inside frame
        frame_pad = max(6, width//100)
        allowed_w = width - 2*frame_pad
        if title_img.size[0] > allowed_w:
            scale = allowed_w / title_img.size[0]
            new_w = allowed_w
            new_h = max(1, int(title_img.size[1] * scale))
            title_img = title_img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
        # Center align title horizontally
        tx = (width - title_img.size[0]) // 2
        # Adjust vertical position so title bottom touches the fixed photo top
        ty_adjusted = ty - title_img.size[1]
        poster.paste(title_img, (tx, ty_adjusted), title_img)

        # Place the square photo at fixed anchor (independent of title height)
        py = photo_top_y
        poster.paste(photo, (px, py))

        # Thin rule under the photo
        rule_y = py + photo_side + int(height*0.02)
        draw.line([(margin_x, rule_y), (width - margin_x, rule_y)], fill=cream, width=max(1, width//400))

        # Artist name vertically on both sides, scaled to fit from photo top to bottom frame
        def fit_vertical_font(text, target_h, start_size, min_size):
            size = start_size
            # Lock artist font to Bahnschrift for consistency
            candidates = ['bahnschrift.ttf']
            while size >= min_size:
                f = _load_font(candidates, size)
                t_w = draw.textbbox((0,0), text, font=f)[2]
                # Add padding fudge so rotation doesn't clip
                pad_fudge = max(4, size // 6)
                if (t_w + 2*pad_fudge) <= target_h:
                    return f
                size -= 1
            return _load_font(candidates, min_size)

        pad = max(6, width//100)
        # Constrain vertical text to not go above the photo top
        target_h = (height - pad) - py
        art_font = fit_vertical_font(artist_u, target_h, start_size=int(width*0.1), min_size=max(14, int(width*0.02)))
        # Ensure album title remains the largest text
        if art_font.size >= heading_font.size:
            safe_size = max(10, heading_font.size - 2)
            art_font = _load_font(['bahnschrift.ttf','arialbd.ttf','segoeuib.ttf','impact.ttf'], safe_size)

        # Render horizontal then rotate for each side
        tw_bbox = draw.textbbox((0,0), artist_u, font=art_font)
        base_w = tw_bbox[2] - tw_bbox[0]
        base_h = tw_bbox[3] - tw_bbox[1]
        pad_v = max(4, art_font.size // 6)
        base_img = Image.new('RGBA', (base_w + 2*pad_v, base_h + 2*pad_v), (0,0,0,0))
        bdraw = ImageDraw.Draw(base_img)
        bdraw.text((pad_v, pad_v), artist_u, font=art_font, fill=text_color)

        allowed_h = height - pad - py

        def _stack_vertical(text, font, color, allowed_height):
            # Determine per-character font size if needed for stacking.
            chars = list(text)
            size = font.size
            line_gap_factor = 1.05
            # If current size too big, reduce until fits.
            while size > 8:
                f = _load_font(['bahnschrift.ttf'], size)
                line_h = int(size * line_gap_factor)
                total_h = len(chars) * line_h
                if total_h <= allowed_height:
                    font_final = f
                    break
                size -= 1
            else:
                font_final = _load_font(['bahnschrift.ttf'], size)
                line_h = int(size * line_gap_factor)
                total_h = len(chars) * line_h
            img_w = max(draw.textbbox((0,0), 'W', font=font_final)[2], int(font_final.size*0.8)) + 4
            img_h = total_h + 4
            v_img = Image.new('RGBA', (img_w, img_h), (0,0,0,0))
            v_draw = ImageDraw.Draw(v_img)
            y_cursor = 2
            for ch in chars:
                v_draw.text((2, y_cursor), ch, font=font_final, fill=color)
                y_cursor += line_h
            return v_img

        # Rotated approach first
        left_rot = base_img.rotate(90, resample=Image.Resampling.BICUBIC, expand=True)
        right_rot = base_img.rotate(-90, resample=Image.Resampling.BICUBIC, expand=True)

        need_stack = False
        if left_rot.size[1] > allowed_h:
            scale = allowed_h / left_rot.size[1]
            # If scale is very small, stacked vertical characters will be clearer.
            if scale < 0.6:
                need_stack = True
            else:
                left_rot = left_rot.resize((max(1, int(left_rot.size[0]*scale)), allowed_h), resample=Image.Resampling.LANCZOS)
                right_rot = right_rot.resize((max(1, int(right_rot.size[0]*scale)), allowed_h), resample=Image.Resampling.LANCZOS)

        if need_stack:
            left_vert = _stack_vertical(artist_u, art_font, text_color, allowed_h)
            right_vert = _stack_vertical(artist_u, art_font, text_color, allowed_h)
        else:
            left_vert = left_rot
            right_vert = right_rot

        # Paste left (bottom-to-top visual style retained by rotation; stacked version already vertical)
        l_x = pad + int(width*0.006)
        l_y = py
        poster.paste(left_vert, (l_x, l_y), left_vert)

        # Paste right
        r_x = width - pad - int(width*0.006) - right_vert.size[0]
        r_y = py
        poster.paste(right_vert, (r_x, r_y), right_vert)

        # Tracklist block: fixed areas for tracks (left) and liner notes (right)
        if tracks is None:
            # Fallback: try to derive tracks locally
            try:
                local_tracks = generate_album_content(pet_info).get('track_list', [])
            except Exception:
                local_tracks = []
        else:
            local_tracks = tracks

        # Normalize track titles and numbers (01., 02., ...)
        norm_tracks = []
        for i, t in enumerate(local_tracks, start=1):
            try:
                # Remove any existing numbering
                title_part = t.split('. ', 1)[1]
            except Exception:
                title_part = t
            norm_tracks.append((i, title_part.upper()))

        tracklist_end_y = rule_y
        notes_end_y = rule_y
        if norm_tracks:
            col_count = 2 if len(norm_tracks) >= 7 else 1
            inner_w = width - 2 * margin_x
            gap = int(width * 0.04)
            tracks_w = inner_w

            # Tracks area rectangle
            t_area_x = margin_x
            t_area_y = rule_y + int(height * 0.02)
            t_area_w = tracks_w
            t_area_h = height - max(6, width//100) - t_area_y

            # Determine rows per column and fit font by width AND height
            rows = (len(norm_tracks)+1)//2 if col_count == 2 else len(norm_tracks)
            longest = max((tt for _, tt in norm_tracks), key=lambda t: len(t)) if norm_tracks else ""

            def fit_track_fonts_box(start_size, min_size):
                size = start_size
                while size >= min_size:
                    bf = _load_font(['segoeui.ttf', 'arial.ttf'], size)
                    nf = _load_font(['bahnschrift.ttf', 'arialbd.ttf', 'segoeui.ttf'], max(int(size*1.08), int(width*0.028)))
                    num_w = draw.textbbox((0,0), "00. ", font=nf)[2]
                    col_w = (t_area_w - (gap if col_count == 2 else 0)) // col_count
                    avail = col_w - num_w - int(width*0.01)
                    lw = draw.textbbox((0,0), longest, font=bf)[2]
                    line_h = int(bf.size * 1.5)
                    need_h = rows * line_h
                    if lw <= avail and need_h <= t_area_h:
                        return bf, nf, line_h
                    size -= 1
                bf = _load_font(['segoeui.ttf','arial.ttf'], min_size)
                nf = _load_font(['bahnschrift.ttf','arialbd.ttf','segoeui.ttf'], int(min_size*1.08))
                return bf, nf, int(bf.size*1.5)

            body_font, num_font, line_h = fit_track_fonts_box(int(width*0.035), int(width*0.02))
            # Cap track fonts so title remains the biggest
            if body_font.size >= heading_font.size:
                new_size = max(10, heading_font.size - 2)
                body_font = _load_font(['segoeui.ttf','arial.ttf'], new_size)
                num_font = _load_font(['bahnschrift.ttf','arialbd.ttf','segoeui.ttf'], max(int(new_size*1.08), int(width*0.028)))
                line_h = int(body_font.size * 1.5)

            for idx, (num, tt) in enumerate(norm_tracks):
                if col_count == 2:
                    col = 0 if idx < (len(norm_tracks)+1)//2 else 1
                    row = idx if col == 0 else idx - (len(norm_tracks)+1)//2
                else:
                    col, row = 0, idx
                col_w = (t_area_w - (gap if col_count == 2 else 0)) // col_count
                x = t_area_x + col * (col_w + gap)
                y = t_area_y + row * line_h
                num_txt = f"{num:02d}. "
                draw.text((x, y), num_txt, font=num_font, fill=text_color)
                nx = x + draw.textbbox((0,0), num_txt, font=num_font)[2]
                draw.text((nx, y), tt, font=body_font, fill=text_color)

            tracklist_end_y = t_area_y + rows * line_h

        # Liner notes under tracklist (ensure visible and non-overlapping)
        notes = (pet_info.get('liner_notes') or '').strip()
        if notes:
            def _wrap_text(draw_ctx, text, font_obj, max_w):
                words = text.split()
                lines, current = [], ''
                for w in words:
                    test = (current + ' ' + w).strip()
                    tw = draw_ctx.textbbox((0,0), test, font=font_obj)[2]
                    if tw <= max_w:
                        current = test
                    else:
                        if current:
                            lines.append(current)
                        current = w
                if current:
                    lines.append(current)
                return lines

            # Dynamically fit notes font to available height to ensure visibility
            def fit_notes_font(start_size, min_size, avail_height):
                size = start_size
                while size >= min_size:
                    nf = _load_font(['segoeui.ttf', 'arial.ttf'], size)
                    gap = int(nf.size * 1.4)
                    # At least one line should fit
                    if avail_height >= gap:
                        return nf, gap
                    size -= 1
                nf = _load_font(['segoeui.ttf', 'arial.ttf'], min_size)
                return nf, int(nf.size * 1.4)

            # Liner notes removed: skip rendering and reserve no area
            lines = []
            available_h = 0

            notes_font, line_gap = fit_notes_font(int(width * 0.03), int(width * 0.018), available_h)
            # No notes to render
            notes_end_y = tracklist_end_y

        # Footer artist repetition removed to avoid duplicate artist text

    # If not Californication style, use the existing vibe/energy layout
    if not cali_typo:
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
            _draw_text_with_spacing(layer_draw, (tx, ty), title_draw, font_title, (0, 0, 0), spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)
            layer = layer.rotate(-4, resample=Image.Resampling.BICUBIC, center=(size//2, int(size*0.15)), expand=False)
            img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
            draw = ImageDraw.Draw(img)
        else:
            tw, th = draw.textbbox((0, 0), title_draw, font=font_title)[2:]
            tx = (width - tw) // 2
            ty = int(height * 0.07)
            _draw_text_with_spacing(draw, (tx+2, ty+2), title_draw, font_title, shadow, spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)
            _draw_text_with_spacing(draw, (tx, ty), title_draw, font_title, (0, 0, 0), spacing=spacing, stroke_width=stroke_w, stroke_fill=stroke_c)

        # Artist position (bottom center)
        aw, ah = draw.textbbox((0, 0), artist, font=font_artist)[2:]
        ax = (width - aw) // 2
        ay = int(height * 0.86)
        draw.text((ax+1, ay+1), artist, font=font_artist, fill=shadow, stroke_width=1, stroke_fill=shadow)
        draw.text((ax, ay), artist, font=font_artist, fill=(0, 0, 0), stroke_width=1, stroke_fill=shadow)

    # Optional stickers based on traits (minimal, simple icons)
    # Pick a sticker font that exists in both branches
    if 'cali_typo' in locals() and cali_typo:
        sticker_font = _load_font(['bahnschrift.ttf', 'arialbd.ttf', 'segoeui.ttf'], int(width * 0.04))
    else:
        # fallback to artist font if available
        try:
            sticker_font = font_artist
        except NameError:
            sticker_font = _load_font(['arialbd.ttf', 'segoeui.ttf', 'arial.ttf'], int(width * 0.04))
    stickers = []
    if pet_info.get('vocalness_description') == 'Opera' or pet_info.get('sneakiness') == 'Master thief':
        stickers.append('Deluxe')
    if pet_info.get('wingman_activity') == 'Park meetups':
        stickers.append('Live at the Park')
    if pet_info.get('wingman_activity') in ('People-watching', 'Bird TV'):
        stickers.append('Window Sessions')

    # Move stickers to bottom-right and stack upward to avoid overlap with tracklist
    sx_right = width - margin_x
    # Place stickers below notes area to avoid overlap; keep within bottom frame
    pad2 = max(6, width//100)
    sy = max(int(height * 0.92), locals().get('tracklist_end_y', int(height*0.85)) + int(height * 0.04))
    sy = min(sy, height - pad2 - int(sticker_font.size))
    for s in stickers[:2]:
        # Draw sticker text only (no box), right-aligned
        sw, sh = draw.textbbox((0, 0), s, font=sticker_font)[2:]
        tx = sx_right - sw
        draw.text((tx, sy), s, font=sticker_font, fill=text_color)
        sy -= sh + 12

    # Save
    # Optional frame for poster mode
    if poster_mode:
        frame = Image.new('RGBA', poster.size, (0,0,0,0))
        fdraw = ImageDraw.Draw(frame)
        border_color = (245, 240, 225)
        pad = max(6, width//100)
        fdraw.rectangle([pad, pad, width-pad, height-pad], outline=border_color, width=pad//2)
        poster = Image.alpha_composite(poster.convert('RGBA'), frame).convert('RGB')

    filename = f"cover_{int(time.time())}_{random.randint(1000,9999)}.jpg"
    out_path = os.path.join(out_dir, filename)
    poster.save(out_path, quality=90)
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

def select_audio_track(pet_info):
    """Select a single 30s preview track based on priority mapping.
    Priority: Quirk > Mischief > Vocalness > Energy/Vibe > Default.
    Returns dict: {file, trait, reason}
    """
    # Normalize inputs
    sig = (pet_info.get('signature_move') or '').strip()
    habit = (pet_info.get('weirdest_habit') or '').strip()
    sneak = (pet_info.get('sneakiness') or '').strip()
    vocal = (pet_info.get('vocalness_description') or '').strip()
    fav_sound = (pet_info.get('favorite_sound') or '').strip()
    energy = (pet_info.get('energy') or '').strip()
    vibe = (pet_info.get('vibe') or '').strip()

    # Quirks (signature move + weirdest habit)
    quirk_map = {
        'Bread loaf': ('quirk_breadloaf.mp3', 'Quirk', 'Bread loaf'),
        'Spooky stare': ('quirk_spooky.mp3', 'Quirk', 'Spooky stare'),
        'Stealing socks': ('quirk_socks.mp3', 'Quirk', 'Stealing socks'),
    }
    for key in (sig, habit):
        if key in quirk_map:
            f, t, r = quirk_map[key]
            return {"file": f, "trait": t, "reason": r}

    # Mischief / Bravery
    if sneak == 'Master thief':
        return {"file": 'mischief_heist.mp3', "trait": 'Mischief', "reason": 'Master thief'}

    # Vocalness
    if vocal == 'Opera':
        return {"file": 'vocal_opera.mp3', "trait": 'Vocalness', "reason": 'Opera'}
    if fav_sound == 'Snorts/bleps':
        return {"file": 'vocal_blep.mp3', "trait": 'Vocalness', "reason": 'Snorts/bleps'}

    # Energy
    if energy == 'Zoomies Every Hour':
        return {"file": 'energy_zoomies.mp3', "trait": 'Energy', "reason": 'Zoomies Every Hour'}
    if energy == 'Chill':
        return {"file": 'energy_chill.mp3', "trait": 'Energy', "reason": 'Chill'}

    # Vibe
    if vibe == 'Regal':
        return {"file": 'vibe_regal.mp3', "trait": 'Vibe', "reason": 'Regal'}
    if vibe == 'Goofball':
        return {"file": 'vibe_goofball.mp3', "trait": 'Vibe', "reason": 'Goofball'}
    if vibe == 'Adventurer':
        return {"file": 'vibe_adventurer.mp3', "trait": 'Vibe', "reason": 'Adventurer'}

    # Default
    return {"file": 'default.mp3', "trait": 'Default', "reason": 'Neutral'}

def map_track_to_stem(title: str) -> str:
    """Map a track title to an audio stem by keywords to match vibe.
    Returns stem name without extension (e.g., 'energy_zoomies').
    """
    t = (title or '').lower()
    # Keyword buckets
    if any(k in t for k in ['zoom', 'sprint', 'turbo', 'midnight zoomies', 'carpet']):
        return 'energy_zoomies'
    if any(k in t for k in ['slow', 'lullaby', 'ballad', 'moon', 'nap', 'sunbeam']):
        return 'energy_chill'
    if any(k in t for k in ['royal', 'throne', 'crown', 'queen', 'prince', 'harp']):
        return 'vibe_regal'
    if any(k in t for k in ['kazoo', 'boop', 'sock', 'goof', 'joke', 'blep']):
        return 'vibe_goofball'
    if any(k in t for k in ['trail', 'odyssey', 'map', 'backyard', 'birds', 'wind', 'voyage']):
        return 'vibe_adventurer'
    if any(k in t for k in ['opera', 'aria', 'solo', 'howl']):
        return 'vocal_opera'
    if any(k in t for k in ['blep', 'snort', 'boing']):
        return 'vocal_blep'
    if any(k in t for k in ['heist', 'caper', 'phantom', 'sneak', 'mission']):
        return 'mischief_heist'
    if any(k in t for k in ['spooky', 'ghost', 'midnight', 'stare']):
        return 'quirk_spooky'
    if any(k in t for k in ['loaf', 'dough', 'yeast']):
        return 'quirk_breadloaf'
    if any(k in t for k in ['sock', 'laundry', 'closet']):
        return 'quirk_socks'
    return 'default'

def build_track_previews(track_list):
    """Create per-track audio preview sources from mapped stems.
    Returns list of {title, sources:[{url,mime}], exists:bool}.
    """
    previews = []
    for track in (track_list or []):
        try:
            title = track.split('. ', 1)[1]
        except Exception:
            title = track
        stem = map_track_to_stem(title)
        # Deterministically pick a variant based on title hash
        h = abs(hash(title))
        variant_idx = (h % 3) + 1  # 1..3 default variants
        # Look for mp3/wav files for this stem
        candidates = []
        for e in ['.mp3', '.wav']:
            fname = f"{stem}_v{variant_idx}{e}"
            p = os.path.join(AUDIO_DIR, fname)
            if os.path.exists(p):
                candidates.append({
                    'url': url_for('static', filename=f'audio/{fname}'),
                    'mime': 'audio/mpeg' if e == '.mp3' else 'audio/wav',
                })
        previews.append({
            'title': title,
            'sources': candidates,
            'exists': len(candidates) > 0,
            'stem': f"{stem}_v{variant_idx}",
        })
    return previews

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
        chosen = name  # Default to just the name if no rules match
    else:
        chosen = random.choice(possible_names)

    # Limit artist name to max 3 words to prevent vertical clipping.
    def _limit_words(text, max_words=3):
        # Preserve ampersands by treating them as separate tokens; remove articles if exceeding limit.
        tokens = text.replace('&', ' & ').split()
        if len(tokens) <= max_words:
            return text
        # Remove filler words first
        filler = {'THE','AND','OF','AT','IN','A','AN','&'}
        prioritized = []
        # Keep first token always
        for tok in tokens:
            up = tok.upper()
            if len(prioritized) >= max_words:
                break
            # Prefer non-filler tokens unless we still have < max_words and only fillers remain.
            if up not in filler or len(prioritized)==0:
                prioritized.append(tok)
        # If we still have fewer than max_words, append remaining non-filler tokens
        if len(prioritized) < max_words:
            for tok in tokens:
                if tok not in prioritized and tok.upper() not in filler:
                    prioritized.append(tok)
                if len(prioritized) >= max_words:
                    break
        # Final safeguard: trim
        return ' '.join(prioritized[:max_words])

    limited = _limit_words(chosen, 3)
    return limited

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
    # Force poster mode and single style
    pet_info['poster_mode'] = 'on'
    pet_info['poster_style'] = 'melodrama'
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
    cover_filename = generate_cover_image(pet_info, saved_path, tracks=content.get('track_list'))
    cover_url = url_for('static', filename=f'generated/{cover_filename}')

    # Single Audio selection (30s preview mapping for poster summary)
    audio_sel = select_audio_track(pet_info)
    # Support .mp3 or .wav; prefer mp3 if present
    chosen_file = audio_sel.get('file') or ''
    stem, ext = os.path.splitext(chosen_file)
    candidates = []
    for e in ['.mp3', '.wav']:
        cand_path = os.path.join(AUDIO_DIR, stem + e)
        if os.path.exists(cand_path):
            candidates.append({
                'url': url_for('static', filename=f'audio/{stem + e}'),
                'mime': 'audio/mpeg' if e == '.mp3' else 'audio/wav',
                'ext': e,
            })
    audio_exists = len(candidates) > 0
    audio_url = candidates[0]['url'] if candidates else None

    # Per-track previews
    track_previews = build_track_previews(content.get('track_list'))

    return render_template(
        'result.html',
        pet_info=pet_info,
        content=content,
        cover_url=cover_url,
        audio_url=audio_url,
        audio_sources=candidates,
        audio_meta=audio_sel,
        audio_exists=audio_exists,
        track_previews=track_previews,
    )

if __name__ == '__main__':
    app.run(debug=True)
