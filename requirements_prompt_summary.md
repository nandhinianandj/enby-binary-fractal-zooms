# Morphogenesis: Deep-Zoom Fractal & Aperiodic Engine

## Project Requirements & Iterative Prompt Summary

This document serves as a complete reference log of the conceptual vision, technical constraints, visual transitions, and iterative refinements specified for the **Morphogenesis (**$10^{35}\times$ **Deep-Zoom)** web application.

## 1. Core Concept & Visual Arc

The foundational idea is an interactive, continuous camera zoom bridging three distinct mathematical and philosophical regimes of order:

1. **Exact Mathematical Self-Similarity (Fractals):** Predictable, infinite recursion (low-to-high algorithmic complexity).

2. **Aperiodic Order (Zero Translational Repetition):** A disconcerting, non-repeating landscape tiled by the 2023 **Einstein "Hat" monotile** (13-sided polykite), representing how continuous space is broken up into discrete, binary (`0` and `1`) human abstractions and urban grids.

3. **Natural & Biological Statistical Self-Similarity:** Dissolving rigid binary boundaries back into organic continuity—zooming from satellite coastlines and beaches into forest treelines, collective human crowds, and microscopic internal human anatomy.

## 2. Technical & Deployment Requirements

* **Pure Client-Side Procedural Generation:** Built entirely in a single self-contained HTML file using vanilla JavaScript, HTML5 2D Canvas, and custom WebGL GLSL fragment shaders (no external image assets or heavy 3D libraries).

* **Deterministic Random Seed Engine (`Mulberry32` PRNG):**

  * Every page reload or click of the **"Mutate Seed"** button generates a unique 32-bit random seed synced to the URL query string (`?seed=`).

  * Each seed mutates the color palette archetype, fractal fold symmetry, Mandelbulb power exponent, Einstein Hat chiral ratio, and coastal Hurst roughness exponent ($H$).

* **Fly.io Cloud Deployment Kit:**

  * Includes an in-app modal containing production-ready, zero-dependency deployment manifests (`server.js`, `package.json`, `Dockerfile`, and `fly.toml`) plus CLI quickstart instructions for hosting on Fly.io Machines.

## 3. User Interface & Interaction Controls

* **Static Colors by Default:** All shader palettes, fractal bands, and Einstein tiles remain chromatically locked to the geometry by default (`Static (Locked)`), with an optional toggle to enable time-based color drift.

* **Auto-Zoom Transport & Manual Override:**

  * Starts stationary at `Z = 0.0` with a prominent **"▶ Start Auto-Zoom" / "⏸ Pause Auto-Zoom"** button (also bound to `Spacebar`).

  * Includes speed presets (`0.5x`, `1x`, `2x`, `4x`) and a direction toggle (`↓ Dive In` vs. `↑ Pull Out`).

  * Seamless manual zoom via mouse wheel, two-finger touch pinch, or the master `Z` depth scrubber, with a toggleable behavior (`Nudge While Cruising` vs. `Pause Auto on Manual`).

* **Full Bottom UI Collapse:** The **"Hide Details & Configs"** button collapses both the bottom-right Laboratory Control Dock and the bottom-left Concept/Genome/Stepper card (`#infoCard`) for an unobstructed fullscreen view.

* **Live Telemetry & Timing Readouts:** Displays real-time Hausdorff Dimension ($D$), Magnification ($10^0\times \rightarrow 10^{35}\times$), Z-Depth (`0.0 → 927.5`), and elapsed/total runtime (`MM:SS`).

## 4. The 15-Phase Morphogenesis Pipeline & Timing (`Z = 0 → 927.5`)

At the default **`1x` cruise speed (`6.5 Z-units/sec`)**, the complete start-to-end journey takes **2 minutes 22.7 seconds (`142.7s`)**:

### Stage I: Exact Mathematical Fractals (`2D → 3D Raymarched SDF Evolution`)

*Designed to avoid jarring cuts by smoothly extruding and morphing 2D fractals through 3D raymarched signed-distance fields (SDFs) before landing on a flat facet plane.*

1. **Phase 1 — 2D Sierpinski Triangle (`Z = 0.0 → 35.0` | `5.38s`):** Extended recursive self-similar zoom into an exact 2D Sierpinski gasket ($D \approx 1.585$).

2. **Phase 2 — 3D Sierpinski Pyramid (`Z = 35.0 → 75.0` | `6.15s`):** Camera tilts in 3D space as the 2D triangle extrudes into a raymarched 3D Sierpinski Tetrahedron ($D = 2.0$).

3. **Phase 3 — 3D Menger Sponge (`Z = 75.0 → 115.0` | `6.15s`):** Tetrahedral folds morph into the orthogonal cubic cross-tunnels of a 3D Menger Sponge ($D \approx 2.727$).

4. **Phase 4 — 3D Mandelbulb (`Z = 115.0 → 155.0` | `6.15s`):** Blends into a spherical-coordinate 3D Mandelbulb with seed-mutated power exponents.

5. **Phase 5 — Facet Plane Bridge (`Z = 155.0 → 180.0` | `3.85s`):** Zooms directly onto a single flat terrace edge of the 3D fractal until it flattens into a plane etched with seams matching the Einstein Hat tiling.

### Stage II: Aperiodic Monotiles, Binary `0/1` Discretization & 3D Skyline (`45.0s Total`)

*Illustrates how continuous smoothness is broken up by binary `0` and `1` thinking, using the chiral duality of the Einstein Hat (`0` = Dark Unreflected Hat \~85.4%, `1` = Translucent Reflected Anti-Hat \~14.6%, ratio* $1/\phi^4$*), stretched to 15 seconds per phase.*
6. **Phase 6 — Einstein "Hat" Monotile IFS (`Z = 180.0 → 277.5` | `15.00s`):** Feeds the 13-sided Einstein Hat into a contractive Graph-Directed Iterated Function System (IFS) with $H_7/H_8$ fractal supertile boundaries ($\phi^2 \approx 2.618$ inflation), Chaos-Game attractor points, and `0 / 1` binary chiral markers.
7. **Phase 7 — 2.5D Extruded Skyscraper City Skyline (`Z = 277.5 → 375.0` | `15.00s`):** Tilts into an oblique aerial perspective and extrudes the non-repeating `0` and `1` Einstein polygons vertically into a high-rise skyscraper skyline with illuminated window grids, street canyons, rooftop helipads, and spires.
8. **Phase 8 — True 3D Aperiodic Monotiles (`Z = 375.0 → 472.5` | `15.00s`):** Evolves the 2.5D extrusions into true 3D aperiodic polyhedral monotiles (Schmitt–Conway–Danzer twisted bipyramids & Socolar–Taylor 3D honeycombs). Near the harbor waterfront edge, the rigid `0` and `1` binary glyphs soften into `≈` and `∞` continuity symbols and dissolve into the ocean.

### Stage III: Natural & Biological Continuity (`Coast → Crowd → Brain → Lungs`)

*Demonstrates that biologically and physically, the world is continuous again—moving from macroscopic geography to collective human gatherings and internal physiological fractals.*
9. **Phase 9 — Waterfront Coastline & Bathymetric Charts (`Z = 472.5 → 532.5` | `9.23s`):** Seamless transition from the waterfront city edge into an orbital satellite coastline overlaid with nautical hydrographic and bathymetric chart isolines.
10. **Phase 10 — Sandy Beach Swash Zone & Forest Treeline Canopy (`Z = 532.5 → 612.5` | `12.31s`):** Shoreline-locked zoom into breaking surf foam, wet vs. dry golden beach sand, foredune ripples, and overhead sunlit pine/oak forest crowns.
11. **Phase 11 — Festival / Protest Human Crowd (`Z = 612.5 → 672.5` | `9.23s`):**
\* Starts from a high-altitude top-down drone shot where thousands of tightly packed cranial crowns form a near-gapless sea of heads.
\* Features a 10-shade hair color spectrum (jet black, raven, espresso, chestnut, golden blonde, copper ginger, auburn, silver/grey, and festival neon magenta, teal, and violet).
\* As the camera zooms in, full 3D anatomical primitives emerge (rounded shoulders, collars, ears, noses, raised cheering arms, protest placards, and glowing smartphones).
12. **Phase 12 — Single Human Head & Cranial Crown (`Z = 672.5 → 732.5` | `9.23s`):**
\* Uses a unified exponential camera coordinate locked onto the central hero individual at grid cell `(0,0)` with zero position jump and 1:1 matched hair, skin, and jacket colors.
\* Resolves fine individual hair strands radiating from the Fibonacci crown whorl before turning translucent to reveal the folded cerebral cortex gyri beneath.
13. **Phase 13 — Cerebral Neural & Synaptic Network (`Z = 732.5 → 802.5` | `10.77s`):** Plunges into the brain's connectome of pyramidal neuron somas, branching dendritic arbors, myelinated axons, and traveling synaptic action-potential flashes, sprouting blood-brain barrier micro-vessels at the boundary.
14. **Phase 14 — Human Vascular Network (`Z = 802.5 → 867.5` | `10.00s`):** Travels through bifurcating arterial and venous trees governed by Murray's Law ($r_p^3 = r_1^3 + r_2^3$) and anastomosing capillary beds.
15. **Phase 15 — Pulmonary Lung Alveoli Sacs (`Z = 867.5 → 927.5` | `9.23s`):** Culminates deep inside space-filling polyhedral lung alveoli sacs ($D \approx 2.97$) with pericapillary gas-exchange septa, surfactant sheen, and Pores of Kohn.

## 5. Chronological Prompt & Feedback Log

 1. **Initial Prompt:** Proposed a three-scene visual journey: (1) Mathematical fractals (Sierpinski & Mandelbrot), (2) Aperiodic landscape tiled by the non-repeating Einstein "Hat" monotile, and (3) Natural world fractals zooming into a coastline and tree lines.

 2. **Prompt 2 (WebGL & Seed Variety):** Requested a pure JS/WebGL procedural web app where every page reload starts with a different random seed for novelty and interactive exploration.

 3. **Prompt 3 (Longer Transitions, Mutations & Fly.io):** Asked for longer zoom transitions between stages, richer variations on reload (color, shape, size, complexity), and a deployment bundle for **Fly.io**.

 4. **Prompt 4 (Static Colors & Auto-Zoom Button):** Requested static colors by default (`colorDrift = false`) and a prominent button to start/pause Auto-Zoom while preserving immediate manual zoom override.

 5. **Prompt 5 (Einstein Hat IFS & Photorealistic Beach/Treeline):** Asked to feed the Einstein Hat into an Iterated Function System (IFS) generator for a fractal look without self-similarity, and replaced the sudden fjord-to-Voronoi jump with a continuous satellite coastline $\rightarrow$ sandy beach $\rightarrow$ overhead forest treeline zoom.

 6. **Prompt 6 (3D Fractal Evolution & City Skyline Bridge):**

    * Upgraded Stage I to evolve smoothly: `2D Sierpinski Triangle` $\rightarrow$ `3D Sierpinski Pyramid` $\rightarrow$ `3D Menger Sponge` $\rightarrow$ `3D Mandelbulb` $\rightarrow$ `Flat Facet Plane` into Einstein tiles.

    * Added a `3D Skyscraper City Skyline` bridge between the Einstein tiles and the natural coastline/charts/beach/treeline.

 7. **Prompt 7 (Full Bottom UI Hide, Stretched Timeline & Anatomy):** Requested "Hide Details & Configs" to hide the entire bottom UI, stretched the Einstein Hat $\rightarrow$ Skyline $\rightarrow$ Coast $\rightarrow$ Beach $\rightarrow$ Treeline transition, and added human anatomical vascular networks and lung alveoli zooms.

 8. **Prompt 8 (Festival Crowd, Single Head & Brain Connectome):** Inserted long-distance shots of a human crowd at a protest/festival between the treeline and vascular system, zooming into a single human head, then into a cerebral neural network, vascular system, and lung alveoli.

 9. **Prompt 9 & 10 (Stage I Pacing & 1x Timing Table):** Extended the initial fractals (Phase 1) and requested a complete phase-by-phase timing breakdown at `1x` zoom speed.

10. **Prompt 11 (15s Aperiodic Phases & True 3D Monotiles):** Stretched the Einstein Hat IFS and City Skyline phases to 15 seconds each and added **True 3D Aperiodic Monotiles** (15 seconds) after the 2.5D city extrusions.

11. **Prompt 12 (Binary `0/1` Discretization vs. Biological Continuity):** Clarified the dark vs. translucent light Einstein hats (unreflected `0` vs. reflected `1` chiral orientations) and added a `Binary 0/1` overlay showing continuous space broken into binary thinking before dissolving back into biological continuity.

12. **Prompt 13, 14 & 15 (3D Overhead Crowd Realism, High-Altitude Start, Hair Spectrum & Seamless Single-Head Lock):**

    * Replaced flat concentric ovals with depth-sorted 3D overhead human primitives (shoulders, collars, ears, noses, raised arms, signs, phones).

    * Started the crowd from a much higher overhead altitude so the gaps between heads are tiny, with a 10-shade hair color spectrum.

    * Unified the coordinate space and locked the hero head at cell `(0,0)` so zooming from the crowd into the single head has zero cut or color mismatch.

13. **Prompt 16 (Smooth Beach Crowd Transition & Centralized UI Localization):**

    * Eliminated the abrupt cut-scene transition from coastal aerials into crowd heads by placing the crowd directly on the sunlit golden beach scene.

    * Calibrated the camera shore anchor (`uShoreAnchor`) so the zoom target descends smoothly onto the sandy beach between the turquoise ocean surf and dunes.

    * Added high-altitude beach crowd gathering clusters on the sand, soft directional sunlight shadows cast onto the golden sand under each person, and a seamless cross-dissolve blend between the descending coastline and the close-up beach crowd.

    * Extracted all user-facing UI strings, titles, descriptions, and phase telemetry to a centralized `locales/en.json` dictionary with a dynamic `t()` helper and updated `server.js` static serving.

14. **Prompt 17 (Parallel Dev Endpoint & Multi-File Fly.io Deployment Packaging):**

    * **Parallel Development Endpoint (`/dev` & `/preview`):** Configured zero-dependency HTTP routing in `server.js` to serve `morphogenesis_fractals_aperiodicity_natural_order.html` under `/dev` and `/preview` (`X-Environment: development`, `Cache-Control: no-cache, no-store, must-revalidate`) while serving `index.html` at `/` (`X-Environment: production`).

    * **Fly.io Production & Dev Deployment:** Updated `Dockerfile` to bundle both `index.html`, `morphogenesis_fractals_aperiodicity_natural_order.html`, and `locales/` into the Alpine container. Added `.dockerignore` to keep image builds lean (excluding `.git`, tests, and development caches). Running `fly deploy` deploys both parallel endpoints together.

    * **Visual Environment Badging & Header Navigation:** Added a distinctive `DEV // morphogenesis.html` badge and header toggle links (`Dev (/dev)` in production and `Prod (/)` in development) allowing instantaneous switching between environments.

    * **Automated Playwright Test Suite [8/8]:** Added test coverage asserting `200 OK` status, distinct `X-Environment` headers, JSON endpoint map on `/healthz`, and live DOM rendering of the environment badge.

15. **Prompt 18 (Biologically Realistic Lungs, Bronchial Airway Tree & 3D Alveoli Gas Exchange):**

    * Replaced flat 2D Voronoi polygons and abstract fbm line noise with physiologically authentic, 3D anatomical models inspired by respiratory medical animations (e.g. *The Brain Maze - What Happens During an Asthma Attack*).

    * **Phase 15 (`Z = 900 → 965` | `renderBronchialLungs`):** Bilateral pulmonary lung lobes (Right 3 lobes, Left 2 lobes with cardiac notch) expanding and contracting with rhythmic tidal respiration ($\sim 3.9\text{s}$ cycle), central trachea with ribbed cartilaginous C-rings, carina bifurcation into primary/secondary/tertiary bronchioles via Murray's Law, parallel pulmonary artery/vein triads, and dynamic oxygen airflow streamlines rushing down the airway lumen during inhalation.

    * **Phase 16 (`Z = 965 → 1025` | `renderRealisticAlveoli`):** True 3D bulbous spherical "cluster of grapes" (acini) geometry with analytical 3D spherical surface normals, Blinn-Phong specular glints on moist surfactant fluid, Fresnel membrane rim glow, and inter-alveolar crevice ambient occlusion. Features physical alveolar inflation ($\sim 22\%$ expansion on inhale), 3D pericapillary basket-weave capillary mesh, red blood cells converting from deoxygenated venous purple ($\text{SpO}_2 \approx 75\%$) to arterial scarlet ($\text{SpO}_2 \approx 99\%$), shimmering $\text{O}_2$ molecular diffusion sparks, and Pores of Kohn collateral ventilation apertures.

    * Synchronized all updates across `locales/en.json`, `index.html`, and `morphogenesis_fractals_aperiodicity_natural_order.html`. All 8 automated test suites and 94 button clicks passed cleanly on both Prod and Dev.


