# -*- coding: utf-8 -*-
import argparse
import os
import numpy as np
import soundfile as sf

# Each rule: (time_offset_ratio, speed_multiplier, gain, stereo_pan)
# Mixing sub-1.0 speeds (deeper/slower) with >1.0 speeds (higher/faster)
# creates a full-spectrum, hypnotic texture instead of high-pitched static.
PROFILES = {
    "manual": [
        (0.00, 0.50, 0.80,  0.0),  # Deep sub-octave foundation
        (0.25, 1.00, 0.65, -0.4),  # Original texture, left
        (0.55, 1.25, 0.45,  0.4),  # Subtle harmonic shimmer, right
    ],
    "slow": [
        (0.00, 0.50, 0.85, -0.2),  # Stretched ambient drone
        (0.35, 0.75, 0.70,  0.3),  # Warm lower-mid drift
        (0.65, 1.50, 0.40, -0.6),  # Distant upper fifth
    ],
    "medium": [
        (0.00, 0.66, 0.75, -0.3),  # Grounded lower fifth
        (0.30, 1.00, 0.70,  0.2),  # Core pulse
        (0.55, 1.50, 0.55,  0.6),  # Rising fifth
        (0.75, 2.00, 0.35, -0.7),  # Octave sparkle
    ],
    "fast": [
        (0.00, 0.75, 0.70, -0.2),  # Driving low-mid anchor
        (0.25, 1.25, 0.65,  0.5),  # Forward momentum
        (0.50, 1.50, 0.60, -0.6),  # Polyrhythmic cascade
        (0.70, 2.00, 0.50,  0.8),  # High-velocity shimmer
    ],
}


def transform_audio(audio, speed_factor, gain, pan):
    """Scales time/pitch via linear interpolation (avoids FFT ringing) and pans stereo."""
    new_length = int(len(audio) / speed_factor)
    if new_length < 10:
        return np.zeros((10, 2), dtype=np.float32)

    old_idx = np.linspace(0, len(audio) - 1, len(audio))
    new_idx = np.linspace(0, len(audio) - 1, new_length)
    scaled = np.interp(new_idx, old_idx, audio) * gain

    angle = (pan + 1.0) * (np.pi / 4.0)
    return np.column_stack((scaled * np.cos(angle), scaled * np.sin(angle)))


def normalize_and_saturate(audio, target_rms=0.14):
    """Removes DC offset, brings average loudness up, and soft-clips transient spikes."""
    audio = audio - np.mean(audio, axis=0)
    rms = np.sqrt(np.mean(audio**2))
    if rms > 1e-9:
        audio = audio * (target_rms / rms)
        audio = np.tanh(audio) * 0.90
    return audio


def analyze_seed(data, sr):
    """Extracts duration, percussiveness (crest factor), and brightness (spectral centroid)."""
    duration = len(data) / sr
    rms = np.sqrt(np.mean(data**2)) + 1e-9
    crest_factor = float(np.max(np.abs(data)) / rms)

    # Spectral centroid via rFFT (weighted mean frequency in Hz)
    magnitudes = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), d=1.0 / sr)
    centroid_hz = float(np.sum(magnitudes * freqs) / (np.sum(magnitudes) + 1e-9))

    return {
        "duration": duration,
        "crest_factor": crest_factor,
        "centroid_hz": centroid_hz,
    }


def adapt_for_preservation(data, sr, rules, max_iterations, preserve=0.75):
    """
    Adjusts the seed and fractal rules based on audio analysis so the
    original timbre survives the fractal zoom.
    preserve: 0.0 (wild/abstract) to 1.0 (strictly recognizable)
    """
    stats = analyze_seed(data, sr)
    print(
        f"  [Analysis] Dur: {stats['duration']:.2f}s | "
        f"Crest: {stats['crest_factor']:.1f} | "
        f"Centroid: {stats['centroid_hz']:.0f} Hz"
    )

    # 1. Cap iterations on short clips so pitch doesn't compound 7 octaves
    safe_iters = min(max_iterations, 3 if stats["duration"] < 2.0 else 4)

    # 2. Soften sharp transients (like a blade swish) so stacking doesn't create drums
    seed = data.copy()
    if stats["crest_factor"] > 6.0 and preserve > 0.3:
        fade_len = max(16, int(len(seed) * 0.15 * preserve))
        t = np.linspace(0, np.pi / 2, fade_len)
        seed[:fade_len] *= np.sin(t)
        seed[-fade_len:] *= np.cos(t)

    # 3. Compute safe per-generation speed bounds to keep centroid in audible/recognizable range
    # Target: keep cumulative shift within ~1.5 octaves of original, bounded by [250Hz, 9000Hz]
    min_target_hz = max(250.0, stats["centroid_hz"] / (2.5 - 1.5 * preserve))
    max_target_hz = min(9000.0, stats["centroid_hz"] * (2.5 - 1.5 * preserve))

    min_speed = (min_target_hz / max(stats["centroid_hz"], 1.0)) ** (1.0 / safe_iters)
    max_speed = (max_target_hz / max(stats["centroid_hz"], 1.0)) ** (1.0 / safe_iters)

    # 4. Adapt rules: clamp speeds, preserve an original-pitch anchor, and break rhythmic grids
    adapted_rules = []
    golden_offsets = [0.0, 0.382, 0.618, 0.236, 0.764]

    for idx, (offset, speed, gain, pan) in enumerate(rules):
        if idx == 0:
            # Keep branch 0 anchored at 1.0x so the original timbre stays recognizable
            new_speed = 1.0
        else:
            # Pull speed toward 1.0 based on preserve strength, then clamp to safe spectral bounds
            pulled = 1.0 + (speed - 1.0) * (1.0 - 0.65 * preserve)
            new_speed = float(np.clip(pulled, min_speed, max_speed))

        # Use irrational offsets for percussive sounds to prevent accidental drum beats
        new_offset = golden_offsets[idx % len(golden_offsets)] if stats["crest_factor"] > 6.0 else offset
        adapted_rules.append((new_offset, new_speed, gain, pan))

    print(f"  [Preservation] Capped to {safe_iters} gens | Speeds: {[round(r[1], 2) for r in adapted_rules]}")
    return seed, adapted_rules, safe_iters

def make_seamless_loop(audio, sr, target_duration, crossfade_sec=3.0):
    """Trims or tiles audio to target_duration with an equal-power tail-to-head crossfade."""
    target_samples = int(target_duration * sr)
    fade_samples = min(int(crossfade_sec * sr), target_samples // 3)
    needed_samples = target_samples + fade_samples

    # If the fractal is still shorter than needed, tile it with smooth overlaps
    while len(audio) < needed_samples:
        overlap = min(fade_samples, len(audio) // 3)
        t = np.linspace(0, np.pi / 2, overlap)[:, None]
        fade_out, fade_in = np.cos(t), np.sin(t)

        tail = audio[-overlap:] * fade_out
        head = audio[:overlap] * fade_in
        audio = np.vstack((audio[:-overlap], tail + head, audio[overlap:]))

    # Carve exact loop length and blend the extra tail into the opening
    body = audio[:target_samples].copy()
    tail = audio[target_samples:target_samples + fade_samples]

    t = np.linspace(0, np.pi / 2, fade_samples)[:, None]
    fade_out, fade_in = np.cos(t), np.sin(t)
    body[:fade_samples] = (body[:fade_samples] * fade_in) + (tail * fade_out)

    return normalize_and_saturate(body)


def generate_audio_fractal(
    seed_file,
    output_file,
    mode="manual",
    target_duration=30.0,
    min_iterations=3,
    max_iterations=7,
    crossfade_sec=3.0,
    preserve=True
):
    data, sr = sf.read(seed_file)
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # Initial seed cleanup
    data = data - np.mean(data)
    peak = np.max(np.abs(data))
    if peak == 0 or np.isnan(peak):
        raise ValueError(f"Seed file '{seed_file}' is silent or contains NaNs.")
    data = data / peak
    data, rules, effective_max_iter = adapt_for_preservation(
        data, sr, PROFILES[mode], max_iterations, preserve=preserve
    )
    current_state = np.column_stack((data, data))
    
    rules = PROFILES[mode]
    current_state = np.column_stack((data, data))
    target_samples_with_fade = int((target_duration + crossfade_sec) * sr)

    print(f"[{mode}] Growing fractal (target: {target_duration:.1f}s)...")

    for gen in range(max_iterations):
        # Mix both channels so right-panned branches aren't dropped
        mono_prev = np.mean(current_state, axis=1)
        max_end = len(current_state)
        transformed_branches = []

        for offset_ratio, speed, gain, pan in rules:
            branch = transform_audio(mono_prev, speed, gain, pan)
            start_sample = int(len(current_state) * offset_ratio)
            max_end = max(max_end, start_sample + len(branch))
            transformed_branches.append((start_sample, branch))

        # Cap canvas size to prevent RAM blowup on long seeds
        max_allowed = int(target_samples_with_fade * 2.5)
        canvas_len = min(max_end, max_allowed)
        next_state = np.zeros((canvas_len, 2), dtype=np.float64)

        for start_sample, branch in transformed_branches:
            if start_sample >= canvas_len:
                continue
            end_sample = min(start_sample + len(branch), canvas_len)
            next_state[start_sample:end_sample] += branch[: end_sample - start_sample]

        current_state = normalize_and_saturate(next_state)
        cur_dur = len(current_state) / sr
        print(f"  Gen {gen + 1}: {cur_dur:.2f}s | RMS: {np.sqrt(np.mean(current_state**2)):.3f}")

        if (gen + 1) >= min_iterations and len(current_state) >= target_samples_with_fade:
            break

    final_loop = make_seamless_loop(current_state, sr, target_duration, crossfade_sec)


    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    final_loop = np.ascontiguousarray(final_loop, dtype=np.float32)

    if output_file.lower().endswith(".ogg"):
        # Write in chunks to avoid the libsndfile/libvorbis single-call segfault
        chunk_size = 65536
        with sf.SoundFile(
            output_file, mode="w", samplerate=sr, channels=2, format="OGG", subtype="VORBIS"
        ) as f:
            for start in range(0, len(final_loop), chunk_size):
                f.write(final_loop[start : start + chunk_size])
    else:
        sf.write(output_file, final_loop, sr, subtype="PCM_16")

    print(f"  Saved -> {output_file} ({len(final_loop)/sr:.2f}s seamless loop)\n")


def main():
    import sys

    parser = argparse.ArgumentParser(
        description="Generate seamless fractal audio loops for the WebGL morphogenesis engine."
    )
    parser.add_argument("-i", "--input", required=True, 
                        default="./sounds/inputs/209073__lukesharples__blade-slice2.wav", help="Path to seed audio file (.wav/.ogg/.flac)")
    parser.add_argument("-o", "--output-dir", default="./sounds/outputs", help="Output directory")
    parser.add_argument(
        "-m", "--mode",
        choices=list(PROFILES.keys()) + ["all"],
        default="all",
        help="Zoom speed profile to generate, or 'all' to build the full web asset pack.",
    )
    parser.add_argument("-d", "--duration", type=float, default=30.0, help="Target loop duration in seconds")
    parser.add_argument("--min-iter", type=int, default=3, help="Minimum fractal iterations")
    parser.add_argument("--max-iter", type=int, default=7, help="Maximum fractal iterations")
    parser.add_argument("--crossfade", type=float, default=3.0, help="Seamless loop crossfade in seconds")
    parser.add_argument("--format", choices=["ogg", "wav"], default="ogg", help="Output format (ogg recommended for web)")
    parser.add_argument(
            "-p", "--preserve", type=float, default=0.75,
            help="Timbre preservation strength: 0.0 (abstract) to 1.0 (faithful)"
        )

    args = parser.parse_args()
    modes = list(PROFILES.keys()) if args.mode == "all" else [args.mode]

    print("RAW sys.argv:", sys.argv)
    print("PARSED args:", vars(args))

    for mode in modes:
        # Fix (returns "209073__lukesharples__blade-slice2")
        fname = os.path.splitext(os.path.basename(args.input))[0]
        out_path = os.path.join(args.output_dir, f"morph_{fname}_{mode}_{args.duration}s.{args.format}")
        print(out_path)
        generate_audio_fractal(
            seed_file=args.input,
            output_file=out_path,
            mode=mode,
            target_duration=args.duration,
            min_iterations=args.min_iter,
            max_iterations=args.max_iter,
            crossfade_sec=args.crossfade,
            preserve=args.preserve
            
        )


if __name__ == "__main__":
    main()
