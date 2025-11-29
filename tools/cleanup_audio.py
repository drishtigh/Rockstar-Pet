import os
from pathlib import Path

CURATED = {
    'energy_fast.mp3',
    'energy_chill.mp3',
    'regal_grand.mp3',
    'goofball_quirky.mp3',
    'adventurer_outdoor.mp3',
    'mischief_sneaky.mp3',
    'vocal_opera.mp3',
    'vocal_comic_blep.mp3',
    'cozy_loaf.mp3',
    'spooky_stare.mp3',
    'playful_socks_pizz.mp3',
    'neutral_default.mp3'
}

AUDIO_DIR = Path(__file__).resolve().parent.parent / 'static' / 'audio'

# Known legacy stem prefixes to purge entirely (any extension)
LEGACY_PREFIXES = [
    'quirk_breadloaf', 'quirk_spooky', 'quirk_socks', 'mischief_heist',
    'vibe_regal', 'vibe_goofball', 'vibe_adventurer', 'energy_zoomies',
    'vocal_blep', 'default'
]


def should_delete(path: Path) -> bool:
    name = path.name
    # Delete obvious wav / variant sets for legacy prefixes
    for prefix in LEGACY_PREFIXES:
        if name.startswith(prefix):
            return True
    # Delete any variant suffixes like _v1/_v2/_v3
    if '_v1' in name or '_v2' in name or '_v3' in name:
        return True
    # Delete wav versions of curated names (keep mp3 if present)
    stem_mp3 = name.replace('.wav', '.mp3')
    if stem_mp3 in CURATED and name.endswith('.wav'):
        return True
    # Delete double-extension or malformed curated names after we fix them separately
    if name.endswith('.mp3.mp3'):
        return False  # We'll rename those
    if name == 'goofball_quirky.mp.mp3':
        return False  # rename path
    return False


def rename_malformed(path: Path):
    n = path.name
    if n.endswith('.mp3.mp3'):
        target = AUDIO_DIR / n[:-4]  # remove one .mp3
        if not target.exists():
            path.rename(target)
            print(f"Renamed {n} -> {target.name}")
    elif n == 'goofball_quirky.mp.mp3':
        target = AUDIO_DIR / 'goofball_quirky.mp3'
        if not target.exists():
            path.rename(target)
            print(f"Renamed {n} -> {target.name}")


def main():
    if not AUDIO_DIR.exists():
        print('Audio directory not found:', AUDIO_DIR)
        return

    deleted = []
    renamed = []

    for f in AUDIO_DIR.iterdir():
        if f.is_file():
            # First rename malformed curated names
            before = f.name
            rename_malformed(f)
            if f.name != before:
                renamed.append((before, f.name))
                continue  # skip deletion logic for renamed entries
            if should_delete(f):
                f.unlink()
                deleted.append(f.name)

    # Final report
    print('Cleanup complete.')
    if renamed:
        print('Renamed:')
        for b, a in renamed:
            print(f'  {b} -> {a}')
    if deleted:
        print('Deleted legacy files:')
        for d in sorted(deleted):
            print(f'  {d}')
    else:
        print('No legacy files found to delete.')

    # Sanity: list remaining curated status
    remaining = {f.name for f in AUDIO_DIR.iterdir() if f.is_file()}
    missing_curated = sorted(CURATED - remaining)
    if missing_curated:
        print('\nMissing curated audio files (add these for full coverage):')
        for m in missing_curated:
            print(' ', m)

if __name__ == '__main__':
    main()
