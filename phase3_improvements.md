# -*- coding: utf-8 -*-
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.#

#* File Name : phase3_improvements.md
#
#* Purpose :
#
#* Creation Date : 23-11-2026
#
#* Last Modified :
#
#* Created By : Yaay Nands
#_._._._._._._._._._._._._._._._._._._._._.#

  Phase 3 Realism Improvement Plan 

 Fractal dimensions matched to published biology/geomorphology literature
 ──────
 Known Fractal Dimensions (Scientific Reference)
 
  System                                              │ D (measured)                                       │ Source
 ─────────────────────────────────────────────────────┼────────────────────────────────────────────────────┼────────────────────────────────────────────────────
  Coastlines (Britain)                                │ D ≈ 1.25                                           │ Mandelbrot 1967
  Turbulent sea surface                               │ D ≈ 1.4–1.6                                        │ Hurst exponent ~0.6
  Beach sand ripples                                  │ D ≈ 1.1 (1D profile)                               │ Spatial autocorrelation
  Tree canopy (plan view)                             │ D ≈ 1.5–1.8                                        │ Box-counting studies
  Cerebral cortex surface                             │ D ≈ 2.73–2.79                                      │ Blüml 2012, Kesić 2016
  Dendritic arbor (neuron)                            │ D ≈ 1.5–1.7                                        │ Smith 1989, Jelinek 1995
  Purkinje cell                                       │ D ≈ 1.8–1.9                                        │ Caserta 1995
  Brain white matter                                  │ D ≈ 2.65                                           │ DTI studies
  Vascular (arterial tree)                            │ D ≈ 2.7                                            │ Murray's Law cascade
  Pulmonary bronchial tree                            │ D ≈ 2.97 (Weibel model)                            │ Mandelbrot 1982
  Alveolar surface area                               │ D ≈ 2.17                                           │ Weibel 1991
  Alveolar ductal tree                                │ D ≈ 2.8–2.9                                        │ Obert 1994
 ──────
 Per-Phase Issues & Fixes
 
 Phase 10 — Coastline (z 570–630, D target ≈ 1.25)

 Current: Domain-warped fBm with 2 warp passes. Good baseline.
 Issues:

 • Hurst H is passed in as a uniform but not tuned to D=1.25 (need H = 2−D = 0.75 in 2D)
 • No self-affine anisotropy — real coastlines are smoother along-shore than cross-shore
 • Contour lines are uniform spacing; real bathymetric charts have tighter isolines in steeper zones
 
 Fixes:

 • Set H=0.75 for coastline passes (H → fractal_dim = 2−H in 2D)
 • Stretch warp domain anisotropically (factor ~2 along shore axis)
 • Add gradient-magnitude-based isoline density (denser where ∇h is steep)
  ──────
  Phase 11 — Beach & Surf (z 630–710, D target ≈ 1.6)
  
  Current: Voronoi pebbles + anisotropic ripples + Gerstner waves. Decent.
  Issues:
  
  • Wave field is purely sinusoidal-sum — no Pierson-Moskowitz spectral shape
  • Foam is a single smoothstep; real surf foam has fractal laciness (D≈1.3 on crest)
  • No wind-row streaks on water (Langmuir circulation)
  
  Fixes:
  
  • Add fBm warp to wave direction per-pixel (fetch-limited spreading)
  • Foam lace via iterative domain-folding: abs(fbm(...)) < thin_threshold
  • Add faint parallel Langmuir streaks (long sinusoids warped by swell)
  ──────
  Phase 12 — Crowd on Beach (z 710–770)
  
  Current: evalPersonLayer tiles crowd figures over beach sand.
  Issues:
  
  • Figures are radially symmetric blobs — look like pills
  • No perspective foreshortening or ground shadow realism
  • Sand under figures doesn't show footprints
  
  Fixes (scope-limited — deprioritise):
  
  • Elongate figure SDF vertically (aspect ~1:4 head:body)
  • Darken sand in elongated shadow ellipse below each figure

 Phase 13 — Head & Cortical Reveal (z 770–830, D target ≈ 2.73–2.79 cortex)
 
 Current: Circular mask, gyri as sin(x + fbm*5), fissure as abs(x).
 Issues:
 
 • Gyri pattern is uniform sinusoid with fbm perturbation — real cortex has sulci of varying depth and width (self-similar at multiple scales → D≈2.75)         
 • Primary sulci (central, Sylvian) are deeper and wider; secondary/tertiary are finer
 • No colour differentiation between gyrus crown (pink, well-vascularised) and sulcal floor (paler, less perfused)
 
 Fixes:
 
 • Replace single-octave gyri with multi-resolution sulcal pattern: large folds (H=0.3, low freq) + medium gyri (H=0.5) + fine dimpling (H=0.7)
 • Composite sulcalDepth = fbm(p*3,0.3)*0.5 + fbm(p*8,0.5)*0.3 + fbm(p*22,0.7)*0.2
 • Colour: gyrus crown warm pink-red; sulcal floor pale grey-beige; pial vessels thin red threads
 ──────
 Phase 14 — Neural Network (z 830–900, D target dendrite ≈ 1.6, axon ≈ 1.5)
 
 Current: vnoise(np*3 + fbm*2.5) iso-lines as axons, vnoise peaks as soma.
 Issues:
 
 • Axons should branch (IFS/L-system geometry), not appear as iso-contours of random noise
 • Soma (cell body) is too bright/large — real neurons are ~10–20 µm, mostly invisible at this scale
 • No directionality (cortical columns run perpendicular to surface)
 • Myelin sheath on larger axons is bright white
 
 Fixes:
 
 • Use DLA-style branching lines: iterated abs() folding in SDF gives branching geometry
   // Symmetric branching dendrite SDF
   float dendriteSDF(vec2 p) {
       float r = 1e9;
           for (int i = 0; i < 5; i++) {
            p = abs(p) - vec2(0.4, 0.2);
            p *= mat2(0.8, 0.6, -0.6, 0.8);
            r = min(r, abs(p.x) - 0.012 / float(i+1));
        }
        return r;
    }
     
  • Add travelling action-potential pulse: bright flash moves along axon direction
  • Myelinated segments: thick white smoothstep with periodic nodes of Ranvier (dark gaps)


Phase 15 — Bronchial Lungs (z 900–965, D target ≈ 2.97)

Current: 5-iteration folded-abs IFS for bronchial tree; bilateral lobe shapes; trachea C-rings.
Issues:

• 5 iterations → branching terminates at about 5 generations; real lungs have ~23 generations (Weibel)
• Tube radius reduction factor 0.64 per branch; Murray's Law says r₃_parent = r₃_child1 + r₃_child2 → ratio ≈ 0.794 per bifurcation (not 0.64)
• Branching angle is fixed at 45°; real lungs alternate ~35° (major) / ~25° (minor)
• Pleural surface texture missing (smooth glistening membrane)

Fixes:

• Increase iterations to 7, correct radius ratio to 0.794 (tubeW *= 0.794)
• Add asymmetric branching: left and right child branch at different angles
• Pleural highlight: thin specular rim at the lobe boundary ellipse
──────


Phase 16 — Alveoli (z 965–1025, D target surface ≈ 2.17)

Current: Voronoi sphere-packing with Blinn-Phong, capillary weave, O₂ flux, Pores of Kohn.
Issues:

• Alveoli are perfect circles; real alveoli are polyhedral (14-faced Kelvin tetrakaidecahedra)
• Capillary weave is a trig grid; should be an irregular web (Voronoi edges → D≈1.5 in 2D)
• O₂ diffusion dots appear randomly over the sac, not localised to thin-wall regions
• Surfactant film (reduces surface tension) has no visual representation

Fixes:

• Replace circle Voronoi with Voronoi cell SDF: color the edges (septae) bright and cell interior dark-reddish
• Capillary mesh = Voronoi edges at finer scale (×5 zoom)
• Restrict O₂ flux to regions where septum < thin_threshold (thin wall = membrane zone)
• Surfactant sheen: thin iridescent film on the air-facing dome (thin-film interference colours)
──────
Also: Koch Snowflake Phase (new Phase between 1 and 2, or standalone)

 Koch Snowflake / Koch Coastline (D = log4/log3 ≈ 1.2619)

Real Koch snowflake: start equilateral triangle, replace each edge midpoint with outward equilateral bump, recurse.

GLSL approach:

  // Signed distance to Koch snowflake (N iterations)
  // Based on: rotate by 60°, fold, repeat
  float kochSDF(vec2 p, int N) {
      for (int i = 0; i < N; i++) {
          // 6-fold symmetry → fold into fundamental domain
          float a = atan(p.y, p.x);
          a = mod(a + PI/6.0, PI/3.0) - PI/6.0;
          p = length(p) * vec2(cos(a), sin(a));
          // Translate so the edge sits at x=0
          p.x -= 0.5;
          // Fold: reflect points beyond the bump back
          if (p.x > 0.0) {
              p = vec2(p.x - 0.5, abs(p.y) - 0.288);
          }
      }
      return abs(p.x) - 0.004; // thin outline
  }
   
Narrative: Insert as a bridge between Stage I (pure mathematical fractals) and Stage II/III (natural fractals). Show:

• N=0: equilateral triangle
• N=1→6: progressive Koch iterations
• Side panel: "D = ln4/ln3 ≈ 1.2619 — same dimension as the British coastline!"
• Then morph into actual coastline (Phase 10) showing the connection


 Placement options:

• As Phase 5b (between Facet Bridge and Einstein Hat) — Z range 165–180 (5 Z units free)
• As a standalone sub-phase within Phase 10 (opening 8s of aerial coastline view shows Koch construction then transitions)
──────
Implementation Priority

 Priority                         │ Phase                            │ Change                                               │ Effort
──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────────────────────┼──────────────────────────────────
 🔴 High                          │ 14                               │ Dendrite branching SDF (IFS abs-fold)                │ Medium
 🔴 High                          │ 15                               │ Murray's Law radius ratio fix (0.794) + 7 iterations │ Small
 🔴 High                          │ 16                               │ Voronoi-edge capillaries + O₂ localised to septa     │ Medium
 🟡 Med                           │ 13                               │ Multi-res sulcal pattern (3 fbm octave groups)       │ Small
 🟡 Med                           │ 10                               │ Gradient-density bathymetric contours                │ Small
 🟡 Med                           │ 11                               │ Foam laciness via iterative domain-fold              │ Small
 🟢 Low                           │ Koch                             │ New Koch phase with iterative N=0→6                  │ Medium
 🟢 Low                           │ 12                               │ Figure aspect ratio + footprint shadow               │ Small

