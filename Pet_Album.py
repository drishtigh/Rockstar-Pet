
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

if __name__ == '__main__':
    album_data = get_pet_info()
