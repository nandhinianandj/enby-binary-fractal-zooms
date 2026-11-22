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
    parser = argparse.ArgumentParser(
        description="Generate seamless fractal audio loops for the WebGL morphogenesis engine."
    )
    parser.add_argument("-i", "--input", required=True, default="./sounds/inputs/209073__lukesharples__blade-slice2.wav", help="Path to seed audio file (.wav/.ogg/.flac)")
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

    args = parser.parse_args()
    modes = list(PROFILES.keys()) if args.mode == "all" else [args.mode]

    for mode in modes:
        fname = args.input.split('.')[0].split('/')[-1]
        out_path = os.path.join(args.output_dir, f"morph_{fname}_{mode}.{args.format}")
        generate_audio_fractal(
            seed_file=args.input,
            output_file=out_path,
            mode=mode,
            target_duration=args.duration,
            min_iterations=args.min_iter,
            max_iterations=args.max_iter,
            crossfade_sec=args.crossfade,
        )


if __name__ == "__main__":
    main()
