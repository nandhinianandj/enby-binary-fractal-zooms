# -*- coding: utf-8 -*-
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.#

#* File Name : fractal_sound.py
#
#* Purpose :
#
#* Creation Date : 15-11-2026
#
#* Last Modified : Sunday 22 November 2026 01:39:20 PM
#
#* Created By : Yaay Nands
#_._._._._._._._._._._._._._._._._._._._._.#
from pprint import pprint as pp


import numpy as np
import soundfile as sf
from scipy.signal import resample


def transform_audio(audio, speed_factor, gain, pan):
    new_length = int(len(audio) / speed_factor)
    if new_length < 10:
        return np.zeros((10, 2))
    
    # Linear interpolation: faster than FFT resample and avoids transient ringing spikes
    old_idx = np.linspace(0, len(audio) - 1, len(audio))
    new_idx = np.linspace(0, len(audio) - 1, new_length)
    scaled = np.interp(new_idx, old_idx, audio) * gain
    
    angle = (pan + 1.0) * (np.pi / 4.0)
    return np.column_stack((scaled * np.cos(angle), scaled * np.sin(angle)))

#def transform_audio(audio, sr, speed_factor, gain, pan):
#    """Scales time/pitch, adjusts volume, and pans stereo."""
#    # Resample changes both duration and pitch simultaneously (true fractal scaling)
#    new_length = int(len(audio) / speed_factor)
#    if new_length < 10:
#        return np.zeros((10, 2))
#    
#    scaled = resample(audio, new_length) * gain
#    
#    # Apply constant-power stereo panning (-1.0 left to 1.0 right)
#    angle = (pan + 1.0) * (np.pi / 4.0)
#    left = scaled * np.cos(angle)
#    right = scaled * np.sin(angle)
#    
#    return np.column_stack((left, right))

def generate_audio_fractal(seed_file, output_file, iterations=5):
    # Load seed clip and convert to mono float array
    data, sr = sf.read(seed_file)
    if data.ndim > 1:
        data = np.mean(data, axis=1)
        
    # Normalize seed
    data = data / np.max(np.abs(data))
    
    # Start with stereo version of the seed at Iteration 0
    current_state = np.column_stack((data, data))
    
    # DEFINE THE FRACTAL RULE (Iterated Function System)
    # Each tuple is: (time_offset_ratio, speed_multiplier, gain, stereo_pan)
    rules = [
        (0.0,  1.0, 0.75, -0.3),  # Branch 1: Original timing/pitch, slightly quieter, left
        (0.5,  2.0, 0.65,  0.6),  # Branch 2: Halfway through, 2x speed (+1 octave), right
        (0.75, 1.5, 0.55, -0.8),  # Branch 3: 3/4 through, 1.5x speed (+7 semitones/fifth), far left
    ]
    
    print(f"Growing fractal over {iterations} generations...")
    
    for gen in range(iterations):
        # Calculate total length needed for the next generation
        max_end = len(current_state)
        transformed_branches = []
        
        for offset_ratio, speed, gain, pan in rules:
            # Apply the rule to the ENTIRE previous generation
            branch = transform_audio(current_state[:, 0], speed, gain, pan)
            start_sample = int(len(current_state) * offset_ratio)
            end_sample = start_sample + len(branch)
            
            max_end = max(max_end, end_sample)
            transformed_branches.append((start_sample, branch))
            
        # Create blank canvas for the new generation and mix branches in
        next_state = np.zeros((max_end, 2))
        for start_sample, branch in transformed_branches:
            next_state[start_sample:start_sample + len(branch)] += branch
           
        # Mix stereo to mono so right-panned branches aren't dropped
        mono_prev = np.mean(current_state, axis=1)
    
        for offset_ratio, speed, gain, pan in rules:
            branch = transform_audio(mono_prev, speed, gain, pan)

        # Replace raw peak normalization with RMS-target + soft-clipping
        rms = np.sqrt(np.mean(next_state**2))
        if rms > 1e-9:
            next_state = next_state * (0.15 / rms)  # Bring average loudness to a healthy -16 dBFS
            next_state = np.tanh(next_state) * 0.9  # Soft-limit stray crackle spikes without crushing the mixkj
        # Prevent clipping between generations
        peak = np.max(np.abs(next_state))
        if peak > 0:
            next_state = (next_state / peak) * 0.9
            
        current_state = next_state
        print(f"Generation {gen + 1}: {len(current_state)/sr:.2f} seconds")

    sf.write(output_file, current_state, sr)
    print(f"Saved fractal audio to {output_file}")

if __name__ == "__main__":
    # Replace 'seed.wav' with your short sound clip
    generate_audio_fractal("./sounds/inputs/501417__visionear__aachen_burning-fireplace-crackling-fire-sounds.wav", "./sounds/outputs/fractal_output.wav", iterations=5)

