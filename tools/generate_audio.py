#!/usr/bin/env python3
"""
Generate ~30s WAV preview files for Rockstar-Pet without external audio libraries.
Files are written to static/audio/*.wav. If you already have MP3s, keep them;
this script simply provides quick placeholders that align with the quiz mapping.

Filenames generated:
- quirk_breadloaf.wav
- quirk_spooky.wav
- quirk_socks.wav
- mischief_heist.wav
- vocal_opera.wav
- vocal_blep.wav
- energy_zoomies.wav
- energy_chill.wav
- vibe_regal.wav
- vibe_goofball.wav
- vibe_adventurer.wav
- default.wav

Windows PowerShell:
    python .\tools\generate_audio.py
"""
import math
import os
import random
import struct
import sys
import argparse
from typing import List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, 'static', 'audio')
# Defaults (can be overridden by CLI)
SAMPLE_RATE = 44100
DURATION_S = 30.0
FRAMES = int(SAMPLE_RATE * DURATION_S)

# ----------------------
# Low-level DSP helpers
# ----------------------

def clamp(x, lo=-1.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def sine(phase):
    return math.sin(phase)


def square(phase):
    return 1.0 if math.sin(phase) >= 0 else -1.0


def saw(phase):
    # naive saw [-1,1]
    return (phase / math.pi) % 2.0 - 1.0


def white_noise():
    return random.uniform(-1.0, 1.0)


def adsr_env(t, a=0.01, d=0.08, s=0.6, r=0.2, note_len=0.4):
    # very simple ADSR in seconds
    if t < 0 or t > note_len + r:
        return 0.0
    if t <= a:
        return t / a
    t2 = t - a
    if t2 <= d:
        return 1.0 - (1.0 - s) * (t2 / d)
    t3 = t2 - d
    if t3 <= (note_len - a - d):
        return s
    # release
    tr = t3 - (note_len - a - d)
    return s * max(0.0, 1.0 - tr / r)


def write_wav(path: str, data: List[float], sample_rate):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Normalize and convert to 16-bit PCM
    peak = max(1e-6, max(abs(x) for x in data))
    norm = 0.95 / peak
    with open(path, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        byte_count = len(data) * 2 + 36
        f.write(struct.pack('<I', byte_count))
        f.write(b'WAVEfmt ')
        f.write(struct.pack('<I', 16))       # Subchunk1Size (PCM)
        f.write(struct.pack('<H', 1))        # AudioFormat = PCM
        f.write(struct.pack('<H', 1))        # NumChannels = 1 (mono)
        f.write(struct.pack('<I', sample_rate))
        f.write(struct.pack('<I', sample_rate * 2))  # ByteRate = SR * NumCh * Bits/8
        f.write(struct.pack('<H', 2))        # BlockAlign = NumCh * Bits/8
        f.write(struct.pack('<H', 16))       # BitsPerSample
        f.write(b'data')
        f.write(struct.pack('<I', len(data) * 2))
        for x in data:
            s = int(clamp(x * norm) * 32767)
            f.write(struct.pack('<h', s))


def mix_event(buf: List[float], start_idx: int, wave_fn, length_s: float, 
              freq_fn=lambda i, t: 440.0, amp=0.3, env=None):
    length = int(length_s * SAMPLE_RATE)
    for i in range(length):
        idx = start_idx + i
        if 0 <= idx < len(buf):
            t = i / SAMPLE_RATE
            freq = freq_fn(i, t)
            phase = 2 * math.pi * freq * t
            val = wave_fn(phase)
            e = env(t) if env else 1.0
            buf[idx] += val * amp * e


# ----------------------
# Building blocks
# ----------------------

NOTE_FREQS = {
    'C3': 130.81,'D3':146.83,'E3':164.81,'F3':174.61,'G3':196.00,'A3':220.00,'B3':246.94,
    'C4': 261.63,'D4':293.66,'E4':329.63,'F4':349.23,'G4':392.00,'A4':440.00,'B4':493.88,
    'C5': 523.25,'D5':587.33,'E5':659.26,'F5':698.46,'G5':783.99,'A5':880.00,'B5':987.77,
}


def kick(buf, start_idx):
    # pitch drop kick 0.2s
    def freq_fn(i, t):
        return 100.0 * (0.5 ** (t / 0.2)) + 20
    env_fn = lambda t: adsr_env(t, a=0.001, d=0.07, s=0.0, r=0.05, note_len=0.15)
    mix_event(buf, start_idx, sine, 0.2, freq_fn=freq_fn, amp=0.7, env=env_fn)


def snare(buf, start_idx):
    # noise burst 0.12s
    length = int(0.12 * SAMPLE_RATE)
    for i in range(length):
        idx = start_idx + i
        if 0 <= idx < len(buf):
            t = i / SAMPLE_RATE
            env_v = adsr_env(t, a=0.001, d=0.05, s=0.0, r=0.06, note_len=0.09)
            buf[idx] += white_noise() * 0.35 * env_v


def hihat(buf, start_idx):
    # short high noise 0.06s
    length = int(0.06 * SAMPLE_RATE)
    for i in range(length):
        idx = start_idx + i
        if 0 <= idx < len(buf):
            t = i / SAMPLE_RATE
            env_v = adsr_env(t, a=0.001, d=0.02, s=0.0, r=0.03, note_len=0.04)
            # fake high-pass by subtracting smoothed component
            n = white_noise()
            buf[idx] += (n - 0.2 * math.sin(2*math.pi*80*t)) * 0.2 * env_v


def pluck_note(buf, start_idx, note='C4', length_s=0.25, amp=0.25):
    f = NOTE_FREQS.get(note, 440.0)
    env_fn = lambda t: adsr_env(t, a=0.005, d=0.08, s=0.0, r=0.1, note_len=length_s-0.05)
    # Simple two partials to mimic toy/piano-ish
    mix_event(buf, start_idx, sine, length_s, freq_fn=lambda i,t: f, amp=amp, env=env_fn)
    mix_event(buf, start_idx, sine, length_s, freq_fn=lambda i,t: f*2, amp=amp*0.3, env=env_fn)


def bass_note(buf, start_idx, note='C3', length_s=0.5, amp=0.3):
    f = NOTE_FREQS.get(note, 130.81)
    env_fn = lambda t: adsr_env(t, a=0.005, d=0.1, s=0.6, r=0.1, note_len=length_s-0.05)
    mix_event(buf, start_idx, sine, length_s, freq_fn=lambda i,t: f, amp=amp, env=env_fn)


def pad_chord(buf, start_idx, notes, length_s=2.0, amp=0.18):
    env_fn = lambda t: adsr_env(t, a=0.2, d=0.5, s=0.7, r=0.5, note_len=length_s-0.2)
    for n in notes:
        f = NOTE_FREQS.get(n, 440.0)
        mix_event(buf, start_idx, sine, length_s, freq_fn=lambda i,t,f=f: f, amp=amp, env=env_fn)


def glide_sine(buf, start_idx, f0, f1, length_s=0.6, amp=0.25):
    def freq_fn(i,t):
        return f0 + (f1 - f0) * (t / max(1e-6, length_s))
    env_fn = lambda t: adsr_env(t, a=0.02, d=0.1, s=0.7, r=0.1, note_len=length_s-0.05)
    mix_event(buf, start_idx, sine, length_s, freq_fn=freq_fn, amp=amp, env=env_fn)


def noise_rustle(buf, start_idx, length_s=0.25, amp=0.2):
    length = int(length_s * SAMPLE_RATE)
    for i in range(length):
        idx = start_idx + i
        if 0 <= idx < len(buf):
            t = i / SAMPLE_RATE
            env_v = adsr_env(t, a=0.01, d=0.08, s=0.4, r=0.08, note_len=length_s-0.05)
            buf[idx] += white_noise() * amp * env_v


def birds_chirp(buf, start_idx):
    # short chirps around 2-4kHz
    for off in (0.0, 0.12, 0.24):
        s = start_idx + int(off * SAMPLE_RATE)
        glide_sine(buf, s, 3500, 2200, length_s=0.08, amp=0.18)


def wind_noise(buf, start_idx, length_s=2.0, amp=0.08):
    length = int(length_s * SAMPLE_RATE)
    last = 0.0
    alpha = 0.02
    for i in range(length):
        idx = start_idx + i
        if 0 <= idx < len(buf):
            n = white_noise()
            last = (1 - alpha) * last + alpha * n  # simple low-pass noise
            buf[idx] += last * amp


def bell_ping(buf, start_idx, note='E5', length_s=0.3, amp=0.22):
    f = NOTE_FREQS.get(note, 659.26)
    env_fn = lambda t: adsr_env(t, a=0.005, d=0.2, s=0.0, r=0.1, note_len=length_s-0.05)
    mix_event(buf, start_idx, sine, length_s, freq_fn=lambda i,t: f, amp=amp, env=env_fn)
    mix_event(buf, start_idx, sine, length_s, freq_fn=lambda i,t: f*2.0, amp=amp*0.25, env=env_fn)


# ----------------------
# Track recipes (~30s)
# ----------------------

def seconds_to_frames(s):
    return int(s * SAMPLE_RATE)


def make_buffer():
    return [0.0] * FRAMES


def pattern_kick_snare_hh(buf, bpm):
    spb = 60.0 / bpm
    # 4/4 bar: kicks on 1/3, snares on 2/4, hats on 8ths
    t = 0.0
    while t < DURATION_S:
        bar_start = seconds_to_frames(t)
        # hats 8ths
        for i in range(8):
            hihat(buf, bar_start + seconds_to_frames(i * spb/2))
        kick(buf, bar_start + seconds_to_frames(0*spb))
        snare(buf, bar_start + seconds_to_frames(1*spb))
        kick(buf, bar_start + seconds_to_frames(2*spb))
        snare(buf, bar_start + seconds_to_frames(3*spb))
        t += 4 * spb


def walking_bass(buf, bpm, root='C3'):
    spb = 60.0 / bpm
    scale = ['C3','E3','G3','A3','B2','D3','G3','C3']
    time = 0.0
    idx = 0
    while time < DURATION_S:
        note = scale[idx % len(scale)] if root=='C3' else root
        bass_note(buf, seconds_to_frames(time), note, length_s=spb*0.9, amp=0.32)
        time += spb
        idx += 1


def arp_melody(buf, bpm, notes):
    spb = 60.0 / bpm
    step = spb/2
    time = 0.0
    i = 0
    while time < DURATION_S:
        pluck_note(buf, seconds_to_frames(time), notes[i % len(notes)], length_s=step*0.9, amp=0.22)
        time += step
        i += 1


def build_quirk_breadloaf():
    buf = make_buffer()
    bpm = 60
    # soft pad + slow plucks + squelch (low noise bursts)
    for t in range(0, 30, 4):
        pad_chord(buf, seconds_to_frames(t), ['C4','E4','G4'], length_s=3.0, amp=0.15)
    for t in [0,1,2,3, 6,7,8,9, 12,13,14,15, 18,19,20,21, 24,25,26,27]:
        pluck_note(buf, seconds_to_frames(t*0.75), 'C4', length_s=0.35, amp=0.18)
    for t in [5, 10, 20]:
        noise_rustle(buf, seconds_to_frames(t), length_s=0.4, amp=0.12)
    return buf


def build_quirk_spooky():
    buf = make_buffer()
    bpm = 80
    # minor pads + creak (low glide)
    for t in range(0, 30, 3):
        pad_chord(buf, seconds_to_frames(t), ['A3','C4','E4'], length_s=2.5, amp=0.16)
    for t in [4, 11, 18, 25]:
        glide_sine(buf, seconds_to_frames(t), 90, 50, length_s=1.2, amp=0.2)
    return buf


def build_quirk_socks():
    buf = make_buffer()
    bpm = 110
    notes = ['C4','E4','G4','B3']
    arp_melody(buf, bpm, notes)
    for t in [2, 6.5, 12, 17.5, 22, 27.5]:
        noise_rustle(buf, seconds_to_frames(t), length_s=0.25, amp=0.18)
    return buf


def build_mischief_heist():
    buf = make_buffer()
    bpm = 120
    pattern_kick_snare_hh(buf, bpm)
    walking_bass(buf, bpm, root='C3')
    # cha-ching bells
    for t in [5, 13, 21, 28]:
        bell_ping(buf, seconds_to_frames(t), 'E5', 0.25, 0.22)
        bell_ping(buf, seconds_to_frames(t+0.15), 'G5', 0.25, 0.18)
    return buf


def build_vocal_opera():
    buf = make_buffer()
    bpm = 90
    # dramatic swells
    for t in range(0, 30, 4):
        pad_chord(buf, seconds_to_frames(t), ['C4','G4','E4'], length_s=3.2, amp=0.2)
    for t in [2, 10, 18, 26]:
        bell_ping(buf, seconds_to_frames(t), 'A4', 0.4, 0.2)
    return buf


def build_vocal_blep():
    buf = make_buffer()
    # boing + snort
    for t in [1, 5, 9, 13, 17, 21, 25, 29]:
        glide_sine(buf, seconds_to_frames(t), 600, 200, length_s=0.5, amp=0.22)
        noise_rustle(buf, seconds_to_frames(t+0.2), length_s=0.15, amp=0.18)
    return buf


def build_energy_zoomies():
    buf = make_buffer()
    bpm = 180
    pattern_kick_snare_hh(buf, bpm)
    arp_melody(buf, bpm, ['C4','E4','G4','B4','C5','G4'])
    return buf


def build_energy_chill():
    buf = make_buffer()
    bpm = 60
    # ambient pads + light noise
    for t in range(0, 30, 5):
        pad_chord(buf, seconds_to_frames(t), ['C4','E4','A4'], length_s=4.5, amp=0.14)
    for t in range(0, 30, 6):
        wind_noise(buf, seconds_to_frames(t+1), length_s=2.0, amp=0.06)
    return buf


def build_vibe_regal():
    buf = make_buffer()
    bpm = 100
    # simple harp-like gliss: fast upward plucks periodically
    for base_t in [0, 6, 12, 18, 24]:
        seq = ['C4','D4','E4','G4','A4','C5','E5','G5']
        t = base_t
        for n in seq:
            pluck_note(buf, seconds_to_frames(t), n, length_s=0.18, amp=0.2)
            t += 0.12
    for t in range(0, 30, 4):
        pad_chord(buf, seconds_to_frames(t), ['C4','E4','G4'], length_s=3.0, amp=0.12)
    return buf


def build_vibe_goofball():
    buf = make_buffer()
    # kazoo-ish (square) melody + slide whistles
    for t in [0, 0.5, 1.0, 1.5, 3.0, 3.5, 4.0, 4.5, 6.0, 6.5, 7.0, 7.5]:
        # square lead: emulate via rich sine partials
        pluck_note(buf, seconds_to_frames(t), random.choice(['C4','D4','E4','G4']), length_s=0.25, amp=0.22)
    for t in [5, 10, 15, 20, 25]:
        glide_sine(buf, seconds_to_frames(t), 900, 1300, length_s=0.4, amp=0.2)
    return buf


def build_vibe_adventurer():
    buf = make_buffer()
    bpm = 100
    # guitar-like arps + birds + wind
    arp_melody(buf, bpm, ['C4','E4','G4','E4'])
    for t in [2, 8, 14, 20, 26]:
        birds_chirp(buf, seconds_to_frames(t))
    for t in range(0, 30, 7):
        wind_noise(buf, seconds_to_frames(t+2), length_s=2.0, amp=0.07)
    return buf


def build_default():
    buf = make_buffer()
    bpm = 100
    pattern_kick_snare_hh(buf, bpm)
    arp_melody(buf, bpm, ['C4','E4','G4','E4'])
    return buf


RECIPES = {
    'quirk_breadloaf': build_quirk_breadloaf,
    'quirk_spooky': build_quirk_spooky,
    'quirk_socks': build_quirk_socks,
    'mischief_heist': build_mischief_heist,
    'vocal_opera': build_vocal_opera,
    'vocal_blep': build_vocal_blep,
    'energy_zoomies': build_energy_zoomies,
    'energy_chill': build_energy_chill,
    'vibe_regal': build_vibe_regal,
    'vibe_goofball': build_vibe_goofball,
    'vibe_adventurer': build_vibe_adventurer,
    'default': build_default,
}


def main():
    global SAMPLE_RATE, DURATION_S, FRAMES
    parser = argparse.ArgumentParser(description='Generate ~30s WAV previews for Rockstar-Pet')
    parser.add_argument('--only', type=str, default='', help='Comma-separated list of stems to generate (e.g., energy_zoomies,vibe_regal)')
    parser.add_argument('--samplerate', type=int, default=SAMPLE_RATE, help='Sample rate (default 44100)')
    parser.add_argument('--duration', type=float, default=DURATION_S, help='Duration seconds (default 30)')
    args = parser.parse_args()

    SAMPLE_RATE = max(8000, int(args.samplerate))
    DURATION_S = max(5.0, float(args.duration))
    FRAMES = int(SAMPLE_RATE * DURATION_S)

    targets = [k.strip() for k in args.only.split(',') if k.strip()] if args.only else list(RECIPES.keys())

    os.makedirs(AUDIO_DIR, exist_ok=True)
    made = []
    for stem in targets:
        if stem not in RECIPES:
            print(f"Skipping unknown stem: {stem}")
            continue
        print(f"Generating {stem}.wav ...")
        buf = RECIPES[stem]()
        out = os.path.join(AUDIO_DIR, f"{stem}.wav")
        write_wav(out, buf, SAMPLE_RATE)
        made.append(out)
    print("\nDone. Files:")
    for p in made:
        print("  ", p)
    print("\nTip: If you prefer MP3, you can convert with ffmpeg:")
    print("  ffmpeg -y -i input.wav -codec:a libmp3lame -qscale:a 4 output.mp3")


if __name__ == '__main__':
    sys.exit(main())
