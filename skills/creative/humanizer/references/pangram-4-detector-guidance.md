# Pangram 4: detector-aware editorial guidance

Use this reference when a user names Pangram, supplies Pangram segment results, or asks for detector-driven revision. It updates older folklore about “perplexity,” “burstiness,” and surface-level detector evasion.

## What Pangram 4 actually models

Pangram describes Pangram 4 as a supervised deep-learning classifier, not a perplexity or burstiness meter. Its training set pairs licensed human prose with synthetic “mirrors” matched on topic, tone, and style, then adds hard false-positive cases through active learning. The intent is to make topic, register, and simple stylistic markers less useful shortcuts for the detector.[1][2]

Pangram 4 uses a sparse mixture-of-experts backbone with four classification heads: a 15-bucket segment estimate of AI involvement, tokenwise provenance labels, a mixed-authorship head, and a separate humanizer probe. Long documents are processed in overlapping 512-token windows. Token predictions are smoothed with a document-level conditional random field, then merged to approximately sentence-level spans. The displayed highlights therefore are not exact word-level forensic boundaries.[1][3]

The auxiliary humanizer head runs only after the primary detector finds AI evidence. A negative or absent humanizer flag is not independent proof that no transformation occurred.[1]

Its three provenance labels are:

- **Human:** human-authored text, including negligible AI contribution such as light copyediting, literal translation, spelling, or grammar fixes.
- **AI-Assisted:** genuinely co-authored or substantially rewritten text where human and model contributions are entangled.
- **AI-Generated:** original open-ended prose produced wholly or predominantly by a model.[1]

The product’s continuous AI-involvement score is not the probability that the displayed label is correct. Its confidence field measures how peaked the model’s internal posterior is, not calibrated certainty about authorship.[1][3]

## Why old “humanizer” tactics do not transfer

Pangram explicitly trains a humanizer head on typo injection, casing changes, synonym substitution, homoglyph attacks, and commercial detector-evasion transformations.[1] Its vendor evaluation reports high recall on humanized AI text, and two independent studies of earlier Pangram versions also found strong performance against their tested humanization methods.[4][5] Those studies do not prove that Pangram 4 will detect every future attack, but they are enough to reject a workflow built around surface noise.

Do not treat these as reliable “human” signals:

- high perplexity, “burstiness,” or forced sentence-length variation
- telegraphic fragments added only to disturb a score
- filler such as “honestly,” “kind of,” or “you know”
- invented quirks, deliberate grammar errors, or coined compounds
- random contractions, italics, punctuation swaps, or markdown entropy
- synonym spinning, translation round-trips, typos, Unicode spaces, or homoglyphs

Pangram’s critique of perplexity-based detection is also useful beyond Pangram: perplexity depends on the comparison model, familiar human text may have low perplexity because it appears in training data, and non-native English can be falsely treated as low-perplexity AI prose.[2] These are vendor arguments, but the practical conclusion is sound: do not use “surprise” as a universal proxy for human authorship.

## The editorial implication: recover authorship, not surface entropy

A detector-aware pass should improve the truth of the writing process, not merely its appearance.

1. **Establish provenance.** Ask what came from the person: notes, outline, prior draft, interview answers, source language, approved phrases, lived details, or a real voice sample.
2. **Preserve the human substrate.** Restore the author’s own wording and decisions where a model over-smoothed them. Keep genuine roughness, repetition, asymmetry, disagreement, and uncertainty.
3. **Remove model-added scaffolding.** Cut generic framing, redundant thesis restatements, stock transitions, empty balance, and explanations the author did not choose.
4. **Do not invent “human” evidence.** If the source lacks real specificity, ask the author for it or mark the gap. A model-written anecdote is still model-written even if it sounds idiosyncratic.
5. **Match the requested preservation contract.** In constrained editing, make only expression-level changes and accept that materially model-rewritten prose may correctly remain **AI-Assisted**.
6. **Use flagged spans as diagnostic pointers, not proof.** Read at least the surrounding paragraph because Pangram’s predictions use document context and are postprocessed into sentence-level segments.
7. **Rescan consistently.** Use the same detector version, the same complete prose input, and the same formatting cleanup. Compare segment labels, not just one headline number.
8. **Stop on truthful provenance and good prose.** A Human result is not proof of human authorship. An AI-Assisted result may be the accurate outcome. If a predominantly AI-generated passage needs to become genuinely human-authored, the author—not another model pass—must make substantive choices and supply original language or material.

## Pangram-specific scan protocol

- Scan at least 50 words of complete-sentence natural-language prose.[1][3]
- Prefer raw text or DOCX over parsed PDF. Remove human-written headers, footers, instructions, reference lists, and unrelated boilerplate before scanning, but keep an untouched master document.[3]
- Treat short replies, code, tables of contents, references, technical manuals, instructions, heavily templated text, and math-dominated passages as outside the model’s primary scope.[3]
- Record: Pangram model version, date, exact input, document label/fractions, relevant segment labels, and whether the humanizer flag fired.
- Do not infer causality from one score change. Context windows and document-level decoding mean a local edit can alter neighboring spans. If the user is doing controlled research, change one variable and keep the rest fixed.
- For consequential decisions, require human review and corroborating process evidence such as drafts, notes, or version history. Pangram itself warns that errors can cause serious harm.[3]

## Evidence limits

Pangram 4’s headline error rates and robustness results are primarily vendor-reported.[1][3] The University of Chicago/NBER study is independent but is a 2025 working paper, was not peer-reviewed at release, and tested an earlier commercial Pangram version on a bounded synthetic benchmark.[4] The University of Maryland ACL paper is peer-reviewed and found an earlier Pangram version competitive with expert human detectors on its 300-article setup, including humanized model output, but that result is not a general guarantee and is not a direct Pangram 4 evaluation.[5]

Detector outputs are probabilistic evidence about textual patterns. They do not establish misconduct, factuality, plagiarism, intent, or a complete history of authorship.

## Sources

[1] Pangram Labs, “Pangram 4 Technical Report” (2026): https://pangram-public.s3.us-east-1.amazonaws.com/pdf/pangram_4_technical_report.pdf

[2] Pangram Labs, “Why Perplexity and Burstiness Fail to Detect AI” (updated 2026): https://www.pangram.com/blog/why-perplexity-and-burstiness-fail-to-detect-ai

[3] Pangram Labs, “Pangram 4 Model Card” (2026): https://www.pangram.com/research/model-card/pangram-4

[4] Brian Jabarian and Alex Imas, “Artificial Writing and Automated Detection,” NBER Working Paper 34223 (2025): https://www.nber.org/papers/w34223

[5] Jenna Russell, Marzena Karpinska, and Mohit Iyyer, “People Who Frequently Use ChatGPT for Writing Tasks Are Accurate and Robust Detectors of AI-Generated Text,” ACL 2025: https://aclanthology.org/2025.acl-long.267/
