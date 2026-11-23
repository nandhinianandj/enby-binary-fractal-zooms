# Deferred concept spec: a human decision over a continuous world

Status: deferred; no implementation is authorized by this spec. This is a design question to resolve after the coastal prelude and boundary transitions in [dev_experience_technical_spec.md](dev_experience_technical_spec.md) have been observed with viewers.

## Question to explore

How can the experience show that people sometimes must make a discrete decision using incomplete, continuously varying information, without claiming that every binary choice is arbitrary or harmful?

## Candidate vignette

At the same seeded coastline, show an illustrative continuous field (default: land elevation relative to water). A person or group must place a boundary for a concrete purpose, such as which beach areas receive a temporary flood warning. Two nearby gathering spots fall on opposite sides of the threshold despite similar underlying conditions. The viewer can move the threshold and see who changes category while the coast and people stay continuous. Show uncertainty or a transition band around the boundary. The choice has a purpose and a cost; the visualization must avoid presenting either threshold as uniquely correct.

This is a fictional demonstration, not flood guidance, a risk model, or an account of a real community. Use neutral language (`included/excluded`, `above/below threshold`) rather than moral labels or arbitrary `good/bad` coloring. People are affected by the classification but are not themselves reduced to `0` or `1` in the final view.

## Interaction hypothesis

An optional pause near the second coastal visit could let the viewer adjust the threshold, compare the continuous field with the resulting binary map, and resume the film. The default auto-zoom path must still tell a complete story without interaction. Show what the line is for, what information it uses, what it omits, and which places change classification when it moves. Support undo/replay and preserve the selected seed while comparing thresholds.

## Questions to settle with a prototype

1. Is a flood-warning boundary the right human-scale decision, or would beach access, conservation, or another choice better fit the art without suggesting false real-world authority?
2. Should the viewer make the decision, watch a fictional decision-maker, or compare both perspectives?
3. What consequence can be shown clearly and respectfully without implying that a toy height field predicts actual harm?
4. What does uncertainty mean in this scene: measurement error, changing water level, model limits, or the difficulty of choosing a threshold? Pick one, label it, and avoid combining them into an unexplained blur.
5. Does the vignette clarify the core idea in a short viewer test, or does it turn the work into a policy simulation?

## Gate for later implementation

Build a small storyboard or throwaway prototype first. Proceed only if viewers can explain both why a discrete decision was needed and what continuous information it discarded. Then specify the chosen scenario, data semantics, interactions, copy, and accessibility behavior before changing the dev HTML.
