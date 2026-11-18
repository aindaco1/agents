# Checking a passage against the film

Use the matching local movie and the strongest available source-language track. A container's language tag can be wrong. Check a short passage before choosing a recognition language. Inspect embedded subtitles, multiple audio streams, and translations already burned into the picture. When working from the SRT alone, describe the result as a text review.

```sh
ffprobe -v error -show_streams -show_format -of json "Film.mkv"
# Example for a passage around 00:20:27, after identifying the first audio stream.
ffmpeg -v error -ss 00:20:20 -i "Film.mkv" -map 0:a:0 -t 18 -ac 1 -ar 16000 "passage.wav"
```

**Unclear words.** Listen in context where playback is available. For local speech recognition, run an unprompted source-language pass first. Compare a short original-speed clip with a longer passage that includes the question and reply. For a recurring word, find other occurrences spoken by different characters. Use a filtered or slowed copy if it reveals speech obscured in the original. Retain the original time origin. Slowing changes clip time, and related recognizers can repeat the same error.

**Weigh the evidence.** Check legible credits or signage for spelling, or consult an authoritative written source for that film or dialect when needed. A repeated sound can establish a shared call without settling how to spell it. A following line such as “It'll help you sleep” can establish a pill's purpose while leaving its name unclear. Retain a plausible supplied spelling and timestamp the uncertainty in the notes. Where a damaged fragment is unintelligible, keep the recoverable words and account for any omission. Confirm apparent dialogue in silence, music, crowds or credits before adding it. Label recognition-based checks accurately.

**Mixed languages.** Check the actual language of the passage. Inspect several frames when an on-screen translation can recover dialogue a recognizer missed. Verify OCR against the picture, including accents and line order. If soft subtitles would cover the burned-in text, check placement in the intended player. When a translation for a second language cannot be established, record the interval.

# Diagnosing synchronization

1. Match distinctive spoken lines near the beginning, middle, and end. Record original cue time, observed movie time, and their difference with one signed convention (movie minus subtitle). Use more anchors around suspected changes. Generic greetings, fights and music offer weak matches.
2. A stable difference supports a constant shift. A steadily changing difference can support a rate correction. Fit and check the slope against measured anchors before changing speed. A frame-rate label alone cannot establish a conversion. Abrupt jumps suggest edition changes. Compare dialogue on both sides and fit sections individually. Re-anchor after scenes present in just one cut.
3. Use voice activity or a subtitle synchronizer to propose offsets. Verify by meaning when the SRT and movie use different languages. A multi-minute cue spanning unrelated scenes needs reconstruction from dialogue anchors. Mark interpolated internal boundaries as estimates.
4. Validate with additional lines held back from fitting, at the section joins, and after the final edit. Check sequential IDs, nonnegative starts, positive durations, gaps and overlaps. Account for missing scenes by original cue and inspect any clipped or merged dialogue. Preserve text and speaker formatting on a sync-only job. Report the applied shift or slope per section and the distribution of residual errors for the checked anchors.
