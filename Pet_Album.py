import random
import sys

def print_progress(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """
    Call in a loop to create terminal progress bar
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()

def ask_multiple_choice(prompt, options, default_key, question_num, total_questions):
    """Handles multiple choice questions with skip option and progress bar."""
    print_progress(question_num - 1, total_questions, prefix='Progress:', suffix='Complete', length=50)
    print(f"\n{prompt}")
    for key, value in options.items():
        print(f"   {key}) {value}")
    
    while True:
        choice = input(f"Enter the letter of your choice (or press Enter for default: {options[default_key]}): ").upper()
        if not choice:
            return options[default_key]
        if choice in options:
            return options[choice]
        print("Invalid choice. Please try again.")

def ask_text_input(prompt, default, question_num, total_questions, required=False):
    """Handles text input questions with skip option and progress bar."""
    print_progress(question_num - 1, total_questions, prefix='Progress:', suffix='Complete', length=50)
    while True:
        default_text = f"(or press Enter for default: {default})" if default and not required else ""
        response = input(f"\n{prompt} {default_text}: ")
        if response:
            return response
        if not required:
            return default
        print("This information is required.")

def get_pet_info():
    """Gathers information about the user's pet to create an album cover."""
    pet_info = {}
    total_questions = 15 # 12 questions + name + title + photos + liner notes

    print("Welcome to the Pet Album Cover Generator!")
    print("Let's create a rockstar persona for your pet.")
    print("------------------------------------------")

    # --- Basic Info ---
    pet_info['artist_name'] = ask_text_input("What is your pet's name? (This will be the artist name)", None, 1, total_questions, required=True)
    pet_info['album_title'] = ask_text_input("What is the title of this album?", f"{pet_info['artist_name']}'s Greatest Hits", 2, total_questions)

    # --- Questions ---
    question_num = 3
    energy_options = {'A': 'Chill', 'B': 'Balanced', 'C': 'Zoomies Every Hour'}
    pet_info['energy'] = ask_multiple_choice("How energetic is your pet?", energy_options, 'B', question_num, total_questions); question_num += 1

    vibe_options = {'A': 'Regal', 'B': 'Goofball', 'C': 'Adventurer', 'D': 'Snuggler', 'E': 'Bossy', 'F': 'Wise Sage'}
    pet_info['vibe'] = ask_multiple_choice("What's their overall vibe?", vibe_options, 'B', question_num, total_questions); question_num += 1

    social_options = {'A': 'Shy', 'B': 'Selective', 'C': 'Party animal'}
    pet_info['social'] = ask_multiple_choice("How social are they?", social_options, 'B', question_num, total_questions); question_num += 1

    wingman_options = {'A': 'People-watching', 'B': 'Park meetups', 'C': 'Supervising from a distance'}
    pet_info['wingman_activity'] = ask_multiple_choice("Favorite wingman activity?", wingman_options, 'A', question_num, total_questions); question_num += 1

    move_options = {'A': 'Head tilt', 'B': 'Side-eye', 'C': 'Zoomies', 'D': 'Slow blink', 'E': 'Spooky stare', 'F': 'Bread loaf'}
    pet_info['signature_move'] = ask_multiple_choice("Signature move?", move_options, 'A', question_num, total_questions); question_num += 1

    habit_options = {'A': 'Stealing socks', 'B': 'Staring at walls', 'C': 'Herding humans', 'D': 'Vocal monologues'}
    pet_info['weirdest_habit'] = ask_multiple_choice("Weirdest habit?", habit_options, 'B', question_num, total_questions); question_num += 1

    activity_options = {'A': 'Chasing', 'B': 'Fetch', 'C': 'Puzzle toys', 'D': 'Sunbathing', 'E': 'Bird TV', 'F': 'Box forts'}
    pet_info['favorite_activity'] = ask_multiple_choice("Favorite activity?", activity_options, 'D', question_num, total_questions); question_num += 1

    cuddle_options = {'A': 'Only when I decide', 'B': 'Sometimes', 'C': 'Velcro'}
    pet_info['cuddle_factor'] = ask_multiple_choice("Cuddle factor?", cuddle_options, 'B', question_num, total_questions); question_num += 1

    petting_options = {'A': 'Head only', 'B': 'Belly traps', 'C': 'All-access', 'D': "Don't touch the royal"}
    pet_info['petting_rules'] = ask_multiple_choice("Petting rules?", petting_options, 'A', question_num, total_questions); question_num += 1

    sneakiness_options = {'A': 'Law-abiding', 'B': 'Occasional heist', 'C': 'Master thief'}
    sneakiness = ask_multiple_choice("Sneakiness level?", sneakiness_options, 'B', question_num, total_questions); question_num += 1
    pet_info['sneakiness'] = sneakiness
    if sneakiness == 'Master thief': pet_info['mischief'] = 5
    elif sneakiness == 'Occasional heist': pet_info['mischief'] = 3
    else: pet_info['mischief'] = 1

    vocalness_options = {'A': 'Silent film star', 'B': 'Chatty', 'C': 'Opera'}
    vocalness_desc = ask_multiple_choice("Vocalness?", vocalness_options, 'B', question_num, total_questions); question_num += 1
    pet_info['vocalness_description'] = vocalness_desc
    if vocalness_desc == 'Opera': pet_info['vocalness'] = 5
    elif vocalness_desc == 'Chatty': pet_info['vocalness'] = 3
    else: pet_info['vocalness'] = 1
    
    sound_options = {'A': 'Purr/soft chirps', 'B': 'Barks/meows', 'C': 'Snorts/bleps', 'D': 'Dramatic sighs'}
    pet_info['favorite_sound'] = ask_multiple_choice("Favorite sound?", sound_options, 'A', question_num, total_questions); question_num += 1

    # --- Final Steps ---
    print_progress(question_num - 1, total_questions, prefix='Progress:', suffix='Complete', length=50)
    print("\n--- Album Artwork ---")
    photos = []
    for i in range(5):
        photo_path = input(f"Enter the path to photo {i+1} (or press Enter to finish): ")
        if not photo_path:
            break
        photos.append(photo_path)
    pet_info['photos'] = photos
    question_num +=1

    print_progress(question_num - 1, total_questions, prefix='Progress:', suffix='Complete', length=50)
    pet_info['liner_notes'] = ask_text_input("Describe your pet's 'artistic vision' in 2-3 sentences", "A mysterious and profound artist.", question_num, total_questions)
    question_num += 1

    print_progress(total_questions, total_questions, prefix='Progress:', suffix='Complete', length=50)
    print("\n\n--- Album Details Collected ---")
    for key, value in pet_info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    return pet_info

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

if __name__ == '__main__':
    album_data = get_pet_info()
    
    # Generate and display the creative content
    creative_content = generate_album_content(album_data)
    
    print("\n\n--- Generated Album Content ---")
    print("\nTrack List:")
    for track in creative_content['track_list']:
        print(track)
        
    if creative_content['easter_eggs']:
        print("\nEaster Eggs:")
        for egg in creative_content['easter_eggs']:
            print(f"- {egg}")
