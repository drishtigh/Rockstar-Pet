from flask import Flask, render_template, request
import sys
import random

# Assuming the functions from Pet_Album.py are moved here or imported
# For simplicity, I'll include the necessary functions directly in this file.

app = Flask(__name__)

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
    
    return render_template('result.html', pet_info=pet_info, content=content)

if __name__ == '__main__':
    app.run(debug=True)
