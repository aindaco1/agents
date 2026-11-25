# Subtitles from a soundtrack

## Build the track for this cut

Inspect the streams and sample the picture using the [audio and sync guide](audio-and-sync.md). An empty subtitle stream list still leaves open the possibility of burned-in translations. If there is a legible translation, check its coverage and timing against the scene.

For a non-English-only brief, identify the spoken language by passage. Recordings heard in a scene may switch to English while the characters still speak another language over them. For a narration-only brief, follow the narrator. Check meaningful letters, signs and title cards against the picture and style their translations distinctly when the brief includes them.

Retain source words, speaker turns and times on the original film clock before translating. When using speech recognition, pair a speech-focused pass with a listen or independent pass across continuous scene audio. The latter can recover a quiet reply or the start of a line clipped by a detector. Restore absolute times after trimming or concatenating clips. Use the surrounding exchange to settle who is speaking, how names are used, and where one sentence ends. For competing readings of a dialect, compare the original mix with a longer clip and, if useful, a clearer channel or a dialogue-isolated copy.

## Song lyrics in SRT

When the track includes identifiable sung words, use italics and the single music note `♪` at both ends of the sung passage in each cue. Repeat the markers in each successive lyric cue so a viewer joining mid-song can recognize it. For a lyric that wraps within one cue, put the notes only at the outer ends and keep both lines italicized.

```srt
1
00:00:01,000 --> 00:00:04,000
<i>♪ The tide will turn</i>
<i>and carry us home. ♪</i>

2
00:00:04,200 --> 00:00:07,200
- <i>♪ Carry us home. ♪</i>
- Can you turn that down?
```

In a mixed cue, keep the speaker dashes in their usual positions and style only the sung words. Reserve the lyric markers for words actually sung, including their translation. Keep song titles, descriptions of music, and summaries of an unclear verse in their usual style. If the words are uncertain, check the soundtrack and flag the time. When checking the export, confirm the notes display, italics cover wrapped lyrics, and the next spoken line returns to its intended style.

## Check what the SRT leaves blank

Compare the **exported track** to speech activity from the same audio and time origin. Use independent evidence, such as a voice activity detector run on the original soundtrack. Activity derived only from accepted transcript segments inherits the same omissions. For a full generation pass, include the opening, gaps between cues and the end of the film.

The bundled checker accepts a UTF-8 JSON array of `[start, end]` pairs in seconds, such as `[[12.40, 14.20], [14.55, 16.10]]`. Convert sample indices using the detector's actual sample rate and add the clip origin if applicable. Run from the skill directory.

```sh
python3 scripts/check_srt.py "Film.en.forced.srt" --speech-regions speech.json
```

Review windows are ranked by uncovered speech time. Overlapping detections count once. Bursts at most one second apart within the same subtitle gap are grouped. The default threshold is 1.5 seconds of detected speech per window. Lower it with `--min-uncovered` to inspect short calls or replies. Findings are prompts for playback. English speech, music, crowds and dialogue already translated on screen can all produce legitimate blanks. A visible cue can also cover one speaker while omitting another.

Open candidate windows with enough lead-in and tail to hear the exchange. Sample some unflagged quiet passages and language changes too. If independent speech timings are unavailable, inspect the uncued intervals against the soundtrack directly. Review repeated stock phrases, long strings of syllables and generic greetings that fall over silence or credits. Re-export after edits, rerun the checks and state the scope of playback and any remaining uncertainty.

## Repair a reported omission

1. Reproduce the gap using the exact movie and the sidecar the viewer loaded. Find the previous and next verified spoken cues. Listen and inspect the scene between them, allowing for silence before the missing conversation begins.
2. Recover the turns from the original audio. For a fast or overlapping exchange, compare short clips straddling the turns with a longer uninterrupted reading. Keep only supported wording and timecode the uncertainty. Keep unaffected cue text, styling and times stable while renumbering the export.
3. Replay the entire passage with the corrected SRT selected. Check every new cue and its speaker, then confirm the subtitles clear and the next existing cue still lands correctly. If the same recognition failure is likely elsewhere and the brief allows a wider pass, check similar gaps.
4. Preserve the viewer's sidecar name, including a name they changed after delivery. Compare against the previously delivered version before replacing it. Carry forward independent edits or deliver a distinct revision if they conflict. Reopen the saved file and verify the corrected cues. For requested duplicate copies, compare the bytes at each destination after writing.
