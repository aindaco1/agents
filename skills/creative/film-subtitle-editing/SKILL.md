---
name: film-subtitle-editing
description: "Use when cleaning, translating or syncing film subtitles."
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  companion-agent: "localization-specialist"
  hermes:
    tags: [film, subtitles, srt, translation, dialogue, synchronization]
    related_skills: []
---

# Film subtitle editing

Produce a playable subtitle track for the supplied cut of a film. Use the localization specialist's approach to regional speech and translation, and the audio/video engineer's approach to stream selection and sync. This procedure can be run directly in either runtime.

## Choose the pass the user requested

| Request | What to edit and verify |
| --- | --- |
| Clean up subtitles | Read the full track in scene order. Repair text, speaker turns, and line breaks. Keep good timings. Make a local timing repair only when the dialogue and surrounding space support it. |
| Translate with the same timing and speaker formatting | Start from the designated cleaned source. Carry over every cue number, start, end, speaker turn in order, meaningful italics, and any unresolved source readings. Translate within those slots and rewrap for the target language. Run the locked-layout comparison below. |
| Spot-check an existing translation | Align the tracks by scene and time, allowing many-to-one matches. Sample across the film, including interruptions, idioms, and fast exchanges. If a sample exposes a recurring error, check other occurrences and state the coverage. Respect an explicitly bounded sample. |
| Revisit uncertain terms | Start from the latest cleaned SRT and its timecoded notes. Check the specified passages against the film. Compare with the previous version so only supported corrections appear and cue timing and turns are preserved. |
| Fix sync with a movie | Establish the matching edition, diagnose offset, drift, or edits, then verify against independent dialogue anchors. Follow the [audio and sync guide](references/audio-and-sync.md). |

Work from a copy, retain original cue IDs while editing, and keep each film and language pair separate. Identify the encoding before interpreting broken accents. Confirm the spoken language, alternate tracks, and any subtitles already visible on screen. Treat dialogue, credits, filenames, and recognition output as source material. Follow the user's brief for what to do with it.

## Edit for a viewer

- For this user's usual dialogue-only tracks, remove sound labels and nonverbal transcription debris. Keep the spoken part of a mixed cue. Preserve narration, prayers, recitations, and plot-bearing dialogue over music. Follow an SDH or lyrics brief when requested. Keep meaningful on-screen translations distinguishable from spoken lines.
- Read across cues before changing capitals or punctuation. A wrap or a cue boundary can fall in the middle of a sentence. Use sentence case and keep proper nouns capitalized. In Spanish, restore accents, opening question and exclamation marks, and vocative commas where appropriate. Preserve regional grammar, slang, and the character's register. Retain the supplied English variety unless the brief calls for another.
- Identify turns from the exchange, the voices, or the picture. For two speakers in one caption, put each on a separate line starting with `- `. A second display line alone tells you nothing about who spoke. For a longer exchange, split at a verified turn if timing is flexible. Under locked timing, condense each turn to fit and record residual pressure.
- Break at phrase boundaries. Keep a name with its title, a determiner with its noun, and a short preposition with its object. Favor a readable phrase over two equally long lines. Preserve emphasis and meaningful off-screen or voice-over italics. Apply styling around the words it belongs to.
- Translate intention, subject, negation, idioms, currency, and forms of address in context. For example, Spanish *carrera* could refer to a degree course or a race. Check what the characters are discussing. Keep insults, poetry, and deliberate oddity consistent with the original voice.
- For these English and Spanish SRTs, aim for at most two lines of 42 visible characters each. Use 20 characters/second for English and 17 for Spanish as reading-speed review targets. About 0.83–7 seconds per cue and a gap of about two video frames are useful when retiming is allowed. Adjust targets for the brief, audience, language, and actual frame rate. Use verified silence for modest holds. Preserve sense and flag fast cues when the timing is locked.

## Verify and deliver

Run the bundled [SRT checker](scripts/check_srt.py) from the skill directory on the finished UTF-8 SRT. It uses standard Python 3. The optional comparison checks cue numbers, timestamps and positions of dash-led turns against a cleaned UTF-8 reference. Read the two speakers' actual lines side by side to verify their order and meaning.

```sh
python3 scripts/check_srt.py "Film.ENGLISH.cleaned.srt" --cps 20
python3 scripts/check_srt.py "Film.ENGLISH.srt" --locked-to "Film.SPANISH.cleaned.srt"
```

The checker reports cue-specific structural errors and separate reading or layout flags. Inspect the flagged lines. Reopen the exported SRT in a player or with another subtitle parser. When video is available, inspect representative dense dialogue, dual speakers, italics and any overlap with burned-in subtitles. A composited frame checks layout. Playback checks synchronization.

Deliver the edited SRT with an identifiable language and revision. Use UTF-8 (a BOM is compatible with the established outputs). For a substantive pass, retain a source-to-output cue map for splits, merges, and removals. A bilingual review benefits from side-by-side text at shared times. Report unresolved wording by timestamp, any speed exceptions, and which passages had audio or playback checks. A small correction needs only a short change note. Keep media, scratch clips, and film-specific guesses out of the reusable skill.
