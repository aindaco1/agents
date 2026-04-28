# AVATAR-RULES.md

## Purpose
This file defines the exact generation prompt template and QA checklist used for Hermes Agent avatars.

## CRITICAL
Always embed the full prompt and QA checklist directly in any delegated generation task. Do not tell sub-agents to "read AVATAR-RULES.md".

## Canonical Avatar Prompt
Use this exact structure:

```text
Create a square "headshot" of a distinct human person inspired by historical socialist icon portraiture and agitprop poster design, rendered in punk zine high-contrast scratchy Xerox style matching the approved aesthetic.

STYLE:
- Digital vector illustration
- Historical socialist poster, labor-movement portrait, and protest-flyer influence without copying any specific real person's face
- Agitprop, union-print, constructivist, and underground zine energy
- High contrast as if Xeroxed from a photocopy
- Visible scratches, smudges, toner noise, paper grit, and imperfect reproduction artifacts
- Black, white, whitesmoke, and gray only
- Borderless full bleed, edge-to-edge design

COMPOSITION:
- **CRITICAL: Square 1:1 image -- width MUST equal height exactly and Tight crop: head/shoulders MUST reach image edges**
- The top of the head/hair should touch or be slightly cropped by the top edge; shoulders must extend fully off the bottom and side edges.
- Background base color: #000000
- Background may include subtle role-themed elements, patterns, or scene hints that enhance context, but no legible text and no explicit logos/badges
- Base color must remain clearly dominant and visible
- Background must be full bleed to all edges
- The subject should feel iconic, like a reproduced movement portrait or organizer poster pinned to a wall

CONTENT RULES:
- Exactly one coherent human face (no duplicate faces/features)
- No text, labels, logos, symbols, badges, or watermarks
- No extra panels or poster-like framing
- Expression must be neutral or friendly
- Must NOT look angry, scary, hostile, or mean
- Avoid stereotyped, harmful, or caricatured features
- Skin and clothing must be clearly distinguishable from background color
- The person must read as a distinct individual, not a reused default face template
- Do NOT default to the same glasses, side-part bob, blazer, or face archetype used in other agent avatars
- Use the historical references only as influence for silhouette, posture, and poster-readability; do NOT make an actual portrait or close likeness of any named real person

CHARACTER:
- Name: {DISPLAY_NAME}
- Role: {ROLE_NAME}
- Pronoun/gender cue handling: {GENDER_CUE}
- Historical reference lineage: influenced by the poster-readability of {REF_1}, the silhouette or public presence of {REF_2}, and the movement-print sensibility described as {REF_BLEND}
- Visual variation profile: {VISUAL_PROFILE}
- Distinctive accessories/features: {ACCESSORY_SET}
- Keep high silhouette contrast so avatar is recognizable at very small size
```

## QA Checklist
0. Square dimensions first
- Width must equal height exactly

1. Full-bleed composition
- No border, frame, inset panel, or poster edge
- Background reaches every edge

2. Tight crop
- Head/hair touches or nearly touches the top edge
- Shoulders run off the lower and side edges

3. Single-face integrity
- Exactly one face
- No duplicate or malformed facial features

4. Expression safety
- Neutral or friendly only

5. Xerox/agitation style fidelity
- Strong grayscale Xerox/repro texture
- Reads like a protest poster or zine reproduction

6. Distinct-person check
- Must not look like the same person as adjacent avatars in the batch
- Reject repeated face archetypes, repeated eyewear/hair/blazer combos, or near-duplicate silhouettes

7. Reference-use check
- Historical references should influence iconicity and silhouette only
- Must not read as a direct portrait of the referenced real person

8. Grayscale-only check
- No color accents at all

9. Role readability
- Role cues visible through props, wardrobe, or background hints

10. Thumbnail readability
- Distinct silhouette and face structure still read small

## Save Rule
When an avatar passes QA, save it as `avatar.webp` in the agent folder unless told otherwise.
