import random

def get_pet_info():
    """Gathers information about the user's pet to create an album cover."""

    pet_info = {}

    print("Welcome to the Pet Album Cover Generator!")
    print("Let's create a rockstar persona for your pet.")
    print("------------------------------------------")

    # --- Basic Info ---
    pet_info['artist_name'] = input("What is your pet's name? (This will be the artist name): ")
    pet_info['album_title'] = input("What is the title of this album?: ")

    # --- Energy and Vibe ---
    print("\n--- Energy and Vibe ---")
    energy_options = {
        'A': 'Chill',
        'B': 'Balanced',
        'C': 'Zoomies Every Hour'
    }
    while True:
        print("1. How energetic is your pet?")
        for key, value in energy_options.items():
            print(f"   {key}) {value}")
        energy = input("Enter the letter of your choice: ").upper()
        if energy in energy_options:
            pet_info['energy'] = energy_options[energy]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    vibe_options = {
        'A': 'Regal',
        'B': 'Goofball',
        'C': 'Adventurer',
        'D': 'Snuggler',
        'E': 'Bossy',
        'F': 'Wise Sage'
    }
    while True:
        print("2. What's their overall vibe?")
        for key, value in vibe_options.items():
            print(f"   {key}) {value}")
        vibe = input("Enter the letter of your choice: ").upper()
        if vibe in vibe_options:
            pet_info['vibe'] = vibe_options[vibe]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Social Personality ---
    print("\n--- Social Personality ---")
    social_options = {
        'A': 'Shy',
        'B': 'Selective',
        'C': 'Party animal'
    }
    while True:
        print("3. How social are they?")
        for key, value in social_options.items():
            print(f"   {key}) {value}")
        social = input("Enter the letter of your choice: ").upper()
        if social in social_options:
            pet_info['social'] = social_options[social]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    wingman_options = {
        'A': 'People-watching',
        'B': 'Park meetups',
        'C': 'Supervising from a distance'
    }
    while True:
        print("4. Favorite wingman activity?")
        for key, value in wingman_options.items():
            print(f"   {key}) {value}")
        wingman = input("Enter the letter of your choice: ").upper()
        if wingman in wingman_options:
            pet_info['wingman_activity'] = wingman_options[wingman]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Quirks and Signature Moves ---
    print("\n--- Quirks and Signature Moves ---")
    move_options = {
        'A': 'Head tilt',
        'B': 'Side-eye',
        'C': 'Zoomies',
        'D': 'Slow blink',
        'E': 'Spooky stare',
        'F': 'Bread loaf'
    }
    while True:
        print("5. Signature move?")
        for key, value in move_options.items():
            print(f"   {key}) {value}")
        move = input("Enter the letter of your choice: ").upper()
        if move in move_options:
            pet_info['signature_move'] = move_options[move]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    habit_options = {
        'A': 'Stealing socks',
        'B': 'Staring at walls',
        'C': 'Herding humans',
        'D': 'Vocal monologues'
    }
    while True:
        print("6. Weirdest habit?")
        for key, value in habit_options.items():
            print(f"   {key}) {value}")
        habit = input("Enter the letter of your choice: ").upper()
        if habit in habit_options:
            pet_info['weirdest_habit'] = habit_options[habit]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Play and Hobbies ---
    print("\n--- Play and Hobbies ---")
    activity_options = {
        'A': 'Chasing',
        'B': 'Fetch',
        'C': 'Puzzle toys',
        'D': 'Sunbathing',
        'E': 'Bird TV',
        'F': 'Box forts'
    }
    while True:
        print("7. Favorite activity?")
        for key, value in activity_options.items():
            print(f"   {key}) {value}")
        activity = input("Enter the letter of your choice: ").upper()
        if activity in activity_options:
            pet_info['favorite_activity'] = activity_options[activity]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Affection and Boundaries ---
    print("\n--- Affection and Boundaries ---")
    cuddle_options = {
        'A': 'Only when I decide',
        'B': 'Sometimes',
        'C': 'Velcro'
    }
    while True:
        print("8. Cuddle factor?")
        for key, value in cuddle_options.items():
            print(f"   {key}) {value}")
        cuddle = input("Enter the letter of your choice: ").upper()
        if cuddle in cuddle_options:
            pet_info['cuddle_factor'] = cuddle_options[cuddle]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    petting_options = {
        'A': 'Head only',
        'B': 'Belly traps',
        'C': 'All-access',
        'D': "Don't touch the royal"
    }
    while True:
        print("9. Petting rules?")
        for key, value in petting_options.items():
            print(f"   {key}) {value}")
        petting = input("Enter the letter of your choice: ").upper()
        if petting in petting_options:
            pet_info['petting_rules'] = petting_options[petting]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Bravery and Mischief ---
    print("\n--- Bravery and Mischief ---")
    sneakiness_options = {
        'A': 'Law-abiding',
        'B': 'Occasional heist',
        'C': 'Master thief'
    }
    while True:
        print("10. Sneakiness level?")
        for key, value in sneakiness_options.items():
            print(f"   {key}) {value}")
        sneakiness = input("Enter the letter of your choice: ").upper()
        if sneakiness in sneakiness_options:
            pet_info['sneakiness'] = sneakiness_options[sneakiness]
            if sneakiness == 'C': # Master thief
                 pet_info['mischief'] = 5
            elif sneakiness == 'B': # Occasional heist
                pet_info['mischief'] = 3
            else:
                pet_info['mischief'] = 1
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Communication ---
    print("\n--- Communication ---")
    vocalness_options = {
        'A': 'Silent film star',
        'B': 'Chatty',
        'C': 'Opera'
    }
    while True:
        print("11. Vocalness?")
        for key, value in vocalness_options.items():
            print(f"   {key}) {value}")
        vocalness = input("Enter the letter of your choice: ").upper()
        if vocalness in vocalness_options:
            pet_info['vocalness_description'] = vocalness_options[vocalness]
            if vocalness == 'C': # Opera
                pet_info['vocalness'] = 5
            elif vocalness == 'B': # Chatty
                pet_info['vocalness'] = 3
            else:
                pet_info['vocalness'] = 1
            break
        else:
            print("Invalid choice. Please select one of the options.")

    sound_options = {
        'A': 'Purr/soft chirps',
        'B': 'Barks/meows',
        'C': 'Snorts/bleps',
        'D': 'Dramatic sighs'
    }
    while True:
        print("12. Favorite sound?")
        for key, value in sound_options.items():
            print(f"   {key}) {value}")
        sound = input("Enter the letter of your choice: ").upper()
        if sound in sound_options:
            pet_info['favorite_sound'] = sound_options[sound]
            break
        else:
            print("Invalid choice. Please select one of the options.")

    # --- Photos ---
    print("\n--- Album Artwork ---")
    photos = []
    for i in range(5):
        photo_path = input(f"Enter the path to photo {i+1} (or press Enter to finish): ")
        if not photo_path:
            break
        photos.append(photo_path)
    pet_info['photos'] = photos

    # --- Liner Notes ---
    print("\n--- Artistic Vision ---")
    pet_info['liner_notes'] = input("Describe your pet's 'artistic vision' in 2-3 sentences: ")


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
