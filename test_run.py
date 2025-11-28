import os
from app import generate_cover_image

sample_pet = {
    'vibe': 'Goofball',
    'energy': 'Balanced',
    'favorite_activity': 'Fetch',
    'signature_move': 'Zoomies',
    'favorite_sound': 'Barks/meows',
    'cuddle_factor': 'Velcro',
    'sneakiness': 'Law-abiding',
    'weirdest_habit': 'Vocal monologues',
    'vocalness_description': 'Chatty',
    'social': 'Party animal',
    'poster_style': 'auto'
}

tracks = [
    '1. Track One',
    '2. Track Two',
    '3. Track Three',
    '4. Track Four',
    '5. Track Five',
]

filename = generate_cover_image(sample_pet, photo_path=None, tracks=tracks)
path = os.path.join('static','generated', filename)
print('Generated file:', filename)
print('Exists:', os.path.exists(path))
print('Full path:', os.path.abspath(path))
