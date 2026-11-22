# Fractal Audio Generator (`fractal_sound.py`)

A procedural audio synthesis tool that transforms any short seed recording (e.g., crackling fire, rain, wind, chimes) into lush, seamless stereo soundscapes using an **Iterated Function System (IFS)**. Designed specifically to generate multi-speed, gapless audio loops for the **WebGL Morphogenesis Deep-Zoom Engine**.

---

## Prerequisites

Ensure you have Python 3.8+ installed along with the required audio and numerical libraries:

```bash
pip install numpy soundfile
```

> **Note:** `soundfile` relies on `libsndfile` (bundled automatically on most Windows/macOS wheels). On Linux, if you encounter an import error, install it via your package manager (e.g., `sudo apt install libsndfile1`).

---

## Quick Start

Generate the complete web-ready audio pack (`morph_manual.ogg`, `morph_slow.ogg`, `morph_medium.ogg`, `morph_fast.ogg`) from a single seed file:

```bash
python fractal_sound.py \
  -i ./sounds/inputs/501417__visionear__aachen_burning-fireplace-crackling-fire-sounds.wav \
  -o ./sounds/outputs \
  --mode all \
  --duration 45 \
  --format ogg
```

---

## CLI Arguments

| Flag | Long Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | *(Required)* | Path to the source seed audio file (`.wav`, `.ogg`, `.flac`). |
| `-o` | `--output-dir` | `./sounds/outputs` | Directory where generated audio files will be saved (created automatically if missing). |
| `-m` | `--mode` | `all` | Zoom speed profile to generate: `manual`, `slow`, `medium`, `fast`, or `all`. |
| `-d` | `--duration` | `30.0` | Exact target duration of the final seamless loop, in seconds. |
| | `--min-iter` | `3` | Minimum number of fractal generations to run before checking duration. |
| | `--max-iter` | `7` | Hard cap on fractal generations to prevent excessive compute or memory usage. |
| | `--crossfade` | `3.0` | Length (in seconds) of the equal-power tail-to-head crossfade used to make loops seamless. |
| | `--format` | `ogg` | Output container format (`ogg` recommended for web/Fly.io deployment; `wav` for lossless local testing). |

---

## Sound Profiles (`--mode`)

Each profile defines a distinct set of fractal branching rules combining sub-octave time-stretching (`speed < 1.0`) with harmonic pitch-shifting (`speed > 1.0`) and stereo panning:

* **`manual`** (`morph_manual.*`): Deep sub-octave foundation with gentle stereo width. Ideal as the default ambient bed during manual pan/zoom exploration.
* **`slow`** (`morph_slow.*`): Stretched, meditative drone with warm lower-mid drift and a distant upper fifth. Pairs with slow auto-zoom speeds.
* **`medium`** (`morph_medium.*`): Balanced full-spectrum pulse layering a lower fifth, core texture, rising fifth, and subtle octave shimmer.
* **`fast`** (`morph_fast.*`): Energetic, polyrhythmic cascade with wider stereo movement and bright high-velocity harmonics for rapid deep-zoom flythroughs.

---

## Usage Examples

### 1. Generate a Single Profile for Quick Previewing (WAV)
```bash
python fractal_sound.py \
  -i ./sounds/inputs/fire.wav \
  --mode slow \
  -d 20 \
  --format wav
```

### 2. Deep, Long-Form Ambient Loops (60s with 5s Crossfade)
Useful for Zen mode or prolonged sessions where you want minimal repetition:
```bash
python fractal_sound.py \
  -i ./sounds/inputs/fire.wav \
  -o ./public/audio \
  --mode all \
  -d 60 \
  --crossfade 5.0 \
  --min-iter 4 \
  --format ogg
```

### 3. Denser Fractal Texture (More Iterations)
Force the engine to layer more self-similar generations even if the seed clip is already long:
```bash
python fractal_sound.py \
  -i ./sounds/inputs/fire.wav \
  --mode medium \
  -d 30 \
  --min-iter 5 \
  --max-iter 8
```

---

## Audio Pipeline Highlights

* **Anti-Ringing Resampling:** Uses linear interpolation instead of FFT resampling to avoid Gibbs ringing spikes on percussive/crackling transients.
* **Consistent Loudness:** Removes DC offset, targets a healthy average loudness ($\text{RMS} \approx 0.14$), and applies $\tanh$ soft-clipping so isolated transient spikes never crush the rest of the mix.
* **Gapless Equal-Power Looping:** Automatically grows or smoothly tiles the fractal until it covers `duration + crossfade`, then folds the tail into the opening using a sine/cosine equal-power curve to eliminate clicks and volume dips at the loop boundary.

---

## Web Integration Guide (Web Audio API)

To create a continuous, transformative audio experience alongside the WebGL shaders:

1. **Preload all four `.ogg` tracks** (`morph_manual.ogg`, `morph_slow.ogg`, `morph_medium.ogg`, `morph_fast.ogg`) into `AudioBuffer`s on user interaction (e.g., clicking "Enter" or toggling sound).
2. **Start all four `AudioBufferSourceNode`s simultaneously** with `loop = true`, each routed through its own `GainNode` connected to `audioCtx.destination`.
3. **Crossfade dynamically** as the user changes zoom speed or switches to manual exploration:
   * Set the active mode's `GainNode` to `1.0` and all others to `0.0` using `gain.linearRampToValueAtTime(target, audioCtx.currentTime + 1.8)`.
   * Optionally modulate a master `BiquadFilterNode` (low-pass) or slight `playbackRate` offset tied to the active morphogenesis phase or zoom velocity.