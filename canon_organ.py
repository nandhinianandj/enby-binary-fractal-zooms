# -*- coding: utf-8 -*-
"""
Canon in D — sustained pipe-organ loop generator.

Renders Pachelbel's Canon in D (the "Canon in D" the Stage I phases use) as a
legato pipe-organ arrangement: pedals, sustained swell manual chords and a
cantus firmus melody.  No plucked or percussive attacks are used; every voice
holds through to the next chord, so the loop reads as continuous organ music.

One seamless loop is written per zoom-speed preset.  All loops share the same
tempo and are bar-aligned, so switching speed keeps the harmonic position; only
the number of 8-bar variations (and therefore the loop length) changes.

Usage:
    python3 canon_organ.py -o ./sounds/outputs
    python3 canon_organ.py -o ./sounds/outputs --tempo 60 --format ogg
"""

import argparse
import os
import subprocess
import tempfile
import numpy as np
import soundfile as sf

# ── The ground bass: D A Bm F#m G D G A, one chord per bar ───────────────────
# (pedal / bass note, manual triad voicing close to middle C)
CHORDS = [
    (50, [50, 54, 57]),   # D  : D3  D3 F#3 A3
    (45, [57, 61, 64]),   # A  : A2  A3 C#4 E4
    (47, [59, 62, 66]),   # Bm : B2  B3 D4  F#4
    (42, [54, 57, 61]),   # F#m: F#2 F#3 A3 C#4
    (43, [55, 59, 62]),   # G  : G2  G3 B3  D4
    (38, [50, 54, 57]),   # D  : D2  D3 F#3 A3
    (43, [55, 59, 62]),   # G  : G2  G3 B3  D4
    (45, [57, 61, 64]),   # A  : A2  A3 C#4 E4
]

# First-violin line of the Canon, as half notes (two per bar), MIDI numbers.
MELODY = [
    [78, 76],  # D  : F#5 E5
    [74, 73],  # A  : D5  C#5
    [71, 74],  # Bm : B4  D5
    [69, 73],  # F#m: A4  C#5
    [74, 73],  # G  : D5  C#5
    [71, 69],  # D  : B4  A4
    [67, 66],  # G  : G4  F#4
    [64, 69],  # A  : E4  A4
]

HARMONICS = np.array([1.0, 0.55, 0.34, 0.21, 0.13, 0.08, 0.05, 0.03])
HARMONICS = HARMONICS / HARMONICS.sum()


def midi_to_hz(m):
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


def organ_tone(freq, dur, sr, amp, brightness=1.0, vibrato=0.0,
               detune_cents=3.0, attack=0.045, release=0.22):
    """Additive pipe-organ tone: flat sustain, fast but soft attack, legato release.

    Two slightly detuned ranks give the gentle chorus of a real organ without
    any percussive transient.
    """
    n = max(8, int(round(dur * sr)))
    t = np.arange(n, dtype=np.float64) / sr

    phase_mod = np.zeros(n, dtype=np.float64)
    if vibrato > 0.0:
        phase_mod = (vibrato / (2.0 * np.pi * 5.2)) * np.sin(2.0 * np.pi * 5.2 * t)

    out = np.zeros(n, dtype=np.float64)
    for rank_detune in (-detune_cents, detune_cents):
        f = freq * 2.0 ** (rank_detune / 1200.0)
        for k, h in enumerate(HARMONICS, start=1):
            partial = brightness if k > 1 else 1.0
            out += h * partial * np.sin(2.0 * np.pi * f * k * t + k * phase_mod)

    env = np.ones(n, dtype=np.float64)
    a = min(n, max(4, int(attack * sr)))
    env[:a] = np.sin(np.linspace(0.0, np.pi / 2.0, a)) ** 2
    r = min(n, max(4, int(release * sr)))
    env[-r:] *= np.cos(np.linspace(0.0, np.pi / 2.0, r)) ** 2

    return (out * env * amp).astype(np.float32)


def add_note(buf, midi, start_s, dur_s, sr, amp, **kw):
    """Mix one note into a stereo buffer, wrapping the tail to the loop head."""
    mono = organ_tone(midi_to_hz(midi), dur_s, sr, amp, **kw)
    start = int(round(start_s * sr))
    n = len(buf)
    idx = (start + np.arange(len(mono))) % n
    np.add.at(buf[:, 0], idx, mono)
    np.add.at(buf[:, 1], idx, mono)


def hall_ir(sr, seconds=2.6, seed=7):
    """Smooth, dark hall impulse response (decorrelated stereo)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    t = np.arange(n) / sr
    decay = np.exp(-t * 2.4)
    ir = np.zeros((n, 2), dtype=np.float32)
    for ch in range(2):
        noise = rng.standard_normal(n)
        # One-pole low-pass removes the harsh hi-hat hiss of raw noise.
        for _ in range(2):
            noise = np.convolve(noise, [0.25, 0.5, 0.25], mode="same")
        ir[:, ch] = (noise * decay).astype(np.float32)
    ir /= np.sqrt(np.mean(ir ** 2)) + 1e-9
    return ir


def circular_reverb(dry, ir):
    """FFT convolution that wraps the tail to the head — a gapless loop."""
    n = len(dry)
    wet = np.zeros_like(dry)
    for ch in range(2):
        spec = np.fft.rfft(dry[:, ch]) * np.fft.rfft(ir[:, ch], n=n)
        wet[:, ch] = np.fft.irfft(spec, n=n)
    return wet


def render_loop(variations, tempo, sr):
    beats_per_bar = 4
    beat = 60.0 / tempo
    bar = beats_per_bar * beat
    total = bar * len(CHORDS) * variations
    n = int(round(total * sr))
    buf = np.zeros((n, 2), dtype=np.float32)

    for v in range(variations):
        # The organ builds registration across the Canon: more stops, then an
        # octave doubling of the cantus firmus, then a 4' manual rank.
        pad_amp = 0.055 + 0.010 * v
        mel_amp = 0.085 + 0.012 * v
        bass_amp = 0.075 + 0.008 * v
        bright = min(1.0, 0.55 + 0.15 * v)

        for b, (bass, triad) in enumerate(CHORDS):
            t0 = (v * len(CHORDS) + b) * bar

            add_note(buf, bass, t0, bar + 0.12, sr, bass_amp,
                     brightness=bright, detune_cents=2.0)
            if v >= 2:
                add_note(buf, bass + 12, t0, bar + 0.12, sr, bass_amp * 0.45,
                         brightness=bright, detune_cents=2.0)

            for i, note in enumerate(triad):
                pan_gain = 1.0 - 0.08 * abs(i - 1)
                add_note(buf, note, t0, bar + 0.18, sr, pad_amp * pan_gain,
                         brightness=bright, vibrato=0.06, detune_cents=4.0)
            if v >= 3:
                for note in triad:
                    add_note(buf, note + 12, t0, bar + 0.18, sr, pad_amp * 0.35,
                             brightness=0.45, detune_cents=4.0)

            for h, note in enumerate(MELODY[b]):
                start = t0 + h * (bar / 2.0)
                dur = bar / 2.0 + 0.10
                add_note(buf, note, start, dur, sr, mel_amp,
                         brightness=bright, vibrato=0.18, detune_cents=3.0)
                if v >= 1:
                    add_note(buf, note + 12, start, dur, sr, mel_amp * 0.30,
                             brightness=0.40, vibrato=0.18, detune_cents=3.0)

    wet = circular_reverb(buf, hall_ir(sr))
    mix = buf * 0.70 + wet * 0.32

    mix -= np.mean(mix, axis=0)
    rms = np.sqrt(np.mean(mix ** 2))
    if rms > 1e-9:
        mix = np.tanh(mix * (0.14 / rms)) * 0.90
    return mix


# Speed preset -> number of 8-bar variations.  Faster zoom = shorter loop.
LENGTHS = {
    "slow": 4,   # 0.5x  — full four-variation rendition, ~128 s
    "1x":   3,   # 1x    — three variations, ~96 s
    "2x":   2,   # 2x    — two variations, ~64 s
    "4x":   1,   # 4x    — single variation, ~32 s
}


def main():
    ap = argparse.ArgumentParser(description="Render seamless Canon in D organ loops.")
    ap.add_argument("-o", "--output-dir", default="./sounds/outputs")
    ap.add_argument("-d", "--tempo", type=float, default=60.0,
                    help="quarter-note tempo in BPM (default 60)")
    ap.add_argument("--sr", type=int, default=44100)
    ap.add_argument("--format", default="ogg", choices=["ogg", "wav"])
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    for key, variations in LENGTHS.items():
        audio = render_loop(variations, args.tempo, args.sr)
        duration = len(audio) / args.sr
        name = f"canon_in_d_organ_{key}_{duration:.1f}s.{args.format}"
        path = os.path.join(args.output_dir, name)
        if args.format == "ogg":
            # libsndfile's Vorbis encoder segfaults on multi-minute stereo
            # buffers, so render a temporary WAV and hand it to ffmpeg.
            with tempfile.TemporaryDirectory() as tmp:
                wav = os.path.join(tmp, "loop.wav")
                sf.write(wav, audio, args.sr, format="WAV")
                subprocess.run(
                    ["ffmpeg", "-loglevel", "error", "-y", "-i", wav,
                     "-c:a", "libvorbis", "-q:a", "5", path],
                    check=True,
                )
        else:
            sf.write(path, audio, args.sr, format="WAV")
        print(f"  {key:>4}: {variations} variation(s)  "
              f"{duration:6.1f}s  ->  {path}")


if __name__ == "__main__":
    main()
