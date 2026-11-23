# Dev experience technical spec: continuous world, discrete representations

Status: proposed for implementation in the development HTML only. The production `index.html` remains the reference experience until the dev changes are reviewed. Companion concept spec: [deferred_human_decision_spec.md](deferred_human_decision_spec.md).

## Intent and scope

The viewer should first encounter a living coastal place, then see that place translated into binary tiles, and later return to the same place and its people. The central visual claim is that a discrete representation can be useful while leaving out variation present in the world. This release covers the prelude, a persistent boundary motif, transitions, and accurate language/readouts. It does not implement a consequential human choice.

Work in `morphogenesis_fractals_aperiodicity_natural_order.html` and `locales/en.json` where copy is shared. Keep `/` serving `index.html` and `/dev` serving the development HTML. Changes to shared locale strings must not silently change production copy; use dev-specific copy or a dev-localized override until promotion.

## Sequence and timing

Add a **coastal prelude (P5b)** between existing phase 5 and phase 6. Keep existing phase IDs 1–16 for controls and audio cues. Insert P5b as an explicit segment in the phase registry, with its own title and stepper entry. Increase the Z domain by 130 units, about 20 seconds at 6.5 Z/s. Normal runtime becomes about 2:58. Do not squeeze the prelude into the current 25-unit phase 5.

| Segment | New Z range | Duration at 1× | Content |
|---|---:|---:|---|
| Existing P1–P5 | 0–180 | 27.7 s | Koch/Sierpinski through facet plane |
| New P5b | 180–310 | 20.0 s | Coastline, treeline, beach, people and crowd |
| Existing P6–P9 | 310–700 | 60.0 s | Hat-based binary interpretation, extrusion, city |
| Existing P10–P16 | 700–1155 | 70.0 s | Return to coast, individual, brain, lungs, alveoli |

All existing P6–P16 thresholds shift by +130 Z. For example P6 = 310–407.5, P8 = 505–602.5, P9 = 602.5–700, P10 = 700–760, and P16 = 1095–1155. Preserve each phase's duration. Centralize boundaries in one timeline table used by shader parameters, Canvas overlay, HUD, stepper, scrubber, auto cruise, and audio; eliminate duplicate literal thresholds where practical. A phase jump must land within the intended segment, including P5b. Update normal, slow, fast, and turbo runtime labels from the table.

## Coastal prelude and recurring place

Reuse the existing procedural coast, surf, sand, crowd, and canopy functions where possible. P5b is an **overview of one seeded place**: aerial coastline and bathymetry, beach and treeline, then enough human silhouettes to read as a gathering. It ends back at an aerial scale so the same coast can be abstracted into tiles. The later P10–P12 visit should use the same seed, shoreline anchor, treeline layout, and crowd landmarks; it is a return to that place, not a second unrelated coast. Scrubbing backward must reproduce the same layout. Movement of surf and people can remain time-dependent.

Use an identifiable headland, cove, treeline gap, and crowd cluster as spatial anchors. Render them before and after the Hat passage. Avoid an unexplained hard cut between procedural scenes. During P5b, explicitly show a continuous field such as elevation or distance from the water through color and contour. The field is an illustrative visualization; do not present it as measured geography or risk data.

## Boundary motif and transitions

Introduce one **reference boundary** as a visible line over the coastal field. Initially it follows a contour and varies smoothly with the shore. At the P5b→P6 transition, sample/classify that field into two tile states using a stated threshold. Keep the original contour visible faintly for the first portion of P6 so the loss of detail is visible. The Hat tiling is a visual representation of the sampled field; do not imply the coastline itself becomes tiled. Do not call the threshold a human decision yet.

At P9→P10, reverse the mapping: retain selected tile edges while the same seeded coastal field reappears. Let the reference contour persist over the coast and fade only as the camera approaches the beach. At P10→P12, use a camera move toward the previously visible crowd cluster, maintain the headland/treeline orientation, and reveal person-scale details before removing the aerial map. Keep a recognizable anchor visible through each handoff. Prefer spatial alignment and overlapping imagery to a full-screen color veil. Verify both forward cruise and reverse scrub across each boundary.

The boundary should remain visually distinct from the waterline and bathymetric contours. Legend copy should say, for example, **“Illustrative threshold applied to a continuous field.”** Avoid implying the line has real policy, danger, or biological meaning.

## Precision and language corrections

| Current claim/readout | Dev wording or behavior |
|---|---|
| `Magnification` / `10³⁵×` | Rename to `Journey scale` or `Scene depth`. Show Z progress or a dimensionless relative scale. Remove `10³⁵×` from the page title and HUD unless a coherent camera/world scale model is implemented and tested. |
| `Hausdorff D` for every phase | Display `Model D` only for exact mathematical constructions whose formula applies. For generated coastal, city, crowd, neural, and lung scenes display `Illustrative texture` or a subject label; no numeric D without a specified measurement method and scale range. At Koch→Sierpinski, update the label with the visible construction. |
| `Exact`, `zero-gap`, `true 3D`, named monotile claims | Keep only claims demonstrated by geometry checks. Until then use `Hat-inspired aperiodic patch`, `extruded tile view`, and `3D-inspired forms` where appropriate. Add a validation task if exactness is desired. |
| `Conway's Game of Life` | Use `Life-inspired binary cellular automaton on a tile-neighbor graph`; the current rule uses seven nearest centers, a nonstandard birth condition, and an extra reflected-tile flip. |
| Biological and geographical dimensions | Treat as inspiration or remove from the live HUD. The implementation does not measure fractal dimension of rendered anatomy or coastline. |

Update phase titles, subtitles, Canvas banners, tooltips, embedded English fallback, locale JSON, page title, audio cue labels, and documentation consistently. Phase 1 must name both Koch and Sierpinski; P15/P16 must match the actual lungs/alveoli rendering. Keep the distinction between a **binary model** and the **continuous field it samples** explicit in copy.

## Implementation boundaries

Refactor toward a declarative timeline with segment ID, Z start/end, title, description, readout type, scene weights, and audio cue. Preserve the existing WebGL/Canvas split: WebGL may render the coastal field while Canvas draws Hat tiles and labels. The same `boundary` field/threshold must drive both contour and tile states; a purely decorative line would fail the concept. Ensure drawing order makes the coast visible under the first Hat tiles and vice versa on return. Cache seeded static geometry; avoid rebuilding the whole crowd or tiling per frame.

The existing `/dev` entry point, seed/mutate, scrubber, manual zoom, auto cruise, speed presets, Zen mode, and audio toggle must remain usable. A new scene must not depend on external data or sound to convey the idea. Provide a still-frame or reduced-motion path for viewers who cannot follow fast transitions.

## Acceptance checks

1. At 1×, P5b lasts roughly 20 seconds and visibly includes coastline, treeline, beach, individual people, and a crowd before P6 starts.
2. A viewer can identify the same headland, treeline gap, and crowd cluster on the return in P10–P12; seed reset/replay and reverse scrub preserve their locations.
3. The continuous field, its threshold contour, and the resulting two tile states are simultaneously visible during part of P5b→P6. The inverse relationship is visible during P9→P10.
4. No phase jump, scrub, reverse cruise, or audio cue points to an old Z range. Phase labels, total runtime, and stage highlights agree at every boundary.
5. Neither dev HUD nor banners present a computed `10³⁵×` magnification, measured biological D, standard Conway rule, or validated zero-gap tiling without corresponding evidence.
6. Capture frames and a short video around P5b→P6, P9→P10, and P10→P12 at desktop and phone widths. Check WebGL errors and basic controls on `/dev`. Ask several viewers what changed when the field became tiles; they should describe lost detail or classification without reading a long explanation.

## Open design choices before implementation

- Choose the illustrative field (elevation, shoreline distance, or another spatial gradient). Elevation is the default because the existing coast shader already produces a height field.
- Choose the contour color and whether it remains visible during the city sequence. Default: retain it faintly through P6–P7, then let it recede until the P9 return.
- Decide whether exact Hat tessellation is required. Default: qualify the current geometry and defer exactness validation.
