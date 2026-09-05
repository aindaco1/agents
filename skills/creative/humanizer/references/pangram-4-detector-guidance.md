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

- Treat 50 words as the documented hard floor, not a dependable excerpt length. WIRED reports that Pangram acknowledges weaker performance below 100 words; prefer at least 100 words and the full prose context when available.[1][3][6]
- Authenticate and preserve the exact edition or source file. Prefer raw text or DOCX over parsed PDF; record extraction, OCR, conversion, and cleanup. Remove human-written headers, footers, instructions, reference lists, and unrelated boilerplate before scanning, but keep an untouched master document.[3][6]
- Treat short replies, code, tables of contents, references, technical manuals, instructions, heavily templated text, and math-dominated passages as outside the model’s primary scope.[3]
- Record: Pangram model version, date, exact input, document label/fractions, relevant segment labels, and whether the humanizer flag fired.
- Do not infer causality from one score change. Context windows and document-level decoding mean a local edit can alter neighboring spans. If the user is doing controlled research, change one variable and keep the rest fixed.
- For consequential decisions, require human review and corroborating process evidence such as drafts, notes, or version history. Pangram itself warns that errors can cause serious harm.[3]

## Evidence limits

Pangram 4’s headline error rates and robustness results are primarily vendor-reported.[1][3] The report’s 0.0041% English false-positive rate is 41/1,000,000 FineWeb examples, not a portable guarantee. Its mixed-authorship results are weaker: on 14,990 substantially AI-edited texts, Pangram 4 labeled 41.37% Human, 55.01% Mixed, and 3.62% AI.[1]

The University of Chicago/NBER study is independent but is a 2025 working paper, was not peer-reviewed at release, and tested an earlier commercial Pangram version on a bounded synthetic benchmark.[4] The University of Maryland ACL paper is peer-reviewed and found an earlier Pangram version competitive with expert human detectors on its 300-article setup, including humanized model output, but that result is not a general guarantee and is not a direct Pangram 4 evaluation.[5]

A 2026 Notre Dame paper accepted to the ACM AI Leadership Summit tested **Pangram 3.2**, not Pangram 4, on 642 published abstracts and Gemini 3 Flash rewrites.[7] Pangram flagged 64.4% and 80.1% of its two “refine abstract only” sets; after Undetectable AI v11, fewer than 4% of AI-labeled rewrites remained detected. This shows both policy ambiguity around light editing and one successful evasion condition. It does not establish current Pangram 4 error rates, and a humanizer pass does not change authorship. The acknowledgments thank Pangram for API use.

A separate 2026 working paper scanned 14,419 sales-active self-published genre-fiction ebooks with **Pangram 3.3**.[8] It defined “substantial AI text” as more than 25% of chapter windows receiving a non-Human label and placed 20.0% of its sample in that detector-defined band. The sample excluded titles whose sales rank never beat 1.5 million. WIRED reports that lead author Tuhin Chakrabarty received Pangram API credits, became close friends with founder Max Spero, and has a partner who consults for Pangram. Preserve the detector-defined wording, sample frame, and relationships; do not translate the result into “20% of all self-published books were proven AI-written.”[6]

The often-cited non-native-English bias paper tested seven older detectors on 91 TOEFL essays and 88 US eighth-grade essays.[9] Its 61.22% mean TOEFL false-positive rate is serious, but the study predates Pangram and cannot be reported as a Pangram result. Use it as a fairness warning: require domain-specific validation and never rewrite a person’s register into stereotyped “native” or ornate prose to please a detector.

WIRED’s “gold standard” description is reported market reputation, not a scientific designation.[6] Its profile adds an institutional lesson: even a strong model can cause harm when short excerpts, selective scanning, public callouts, and opaque appeals turn a score into a verdict. Audit the people and process around the model as seriously as the model itself.

Detector outputs are probabilistic evidence about textual patterns. They do not establish misconduct, factuality, plagiarism, intent, or a complete history of authorship.

## Consequential-use protocol

For school, employment, publication, payment, or reputational decisions:

1. Preserve the exact input and report, including version, date, preprocessing, and whether the scan used an excerpt or full context.
2. Seek drafts, notes, tracked changes, source files, and an author explanation.
3. Give the writer notice, the evidence, a chance to respond, and an appeal/correction route.
4. Record why this text was selected for scanning and check whether comparable writers were treated the same way.
5. Do not publicly identify, punish, reject, or terminate someone from detector output alone.

The Gotham Ghostwriters survey cited by WIRED does not supply a misconduct base rate.[10] It was a sponsor-recruited non-probability sample: 61% of 1,190 writing professionals used AI at least sometimes, but only 7% of AI-using professionals said they generated publication text without significant editing. The survey analyzed 291 fiction authors separately. Broad “AI use” includes search, brainstorming, titles, word-finding, outlining, and editing; do not collapse it into undeclared generation.

WIRED’s related reporting documents writers avoiding em dashes or preserving mistakes to look human.[11] Do not operationalize that counterstyle: isolated punctuation, triplets, polished grammar, or roughness are not authorship tests. A first-person account of AI-assisted writing likewise shows that repeated “less clichéd” prompting can exchange one cliché for another; return to the writer’s actual observations and choices instead of recursively polishing model prose.[12]

## Sources

[1] Pangram Labs, “Pangram 4 Technical Report” (2026): https://pangram-public.s3.us-east-1.amazonaws.com/pdf/pangram_4_technical_report.pdf

[2] Pangram Labs, “Why Perplexity and Burstiness Fail to Detect AI” (updated 2026): https://www.pangram.com/blog/why-perplexity-and-burstiness-fail-to-detect-ai

[3] Pangram Labs, “Pangram 4 Model Card” (2026): https://www.pangram.com/research/model-card/pangram-4

[4] Brian Jabarian and Alex Imas, “Artificial Writing and Automated Detection,” NBER Working Paper 34223 (2025): https://www.nber.org/papers/w34223

[5] Jenna Russell, Marzena Karpinska, and Mohit Iyyer, “People Who Frequently Use ChatGPT for Writing Tasks Are Accurate and Robust Detectors of AI-Generated Text,” ACL 2025: https://aclanthology.org/2025.acl-long.267/

[6] Lexi Pandell, “Pangram Has Emerged as the Gold Standard of AI Detection,” WIRED (2026-09-02): https://www.wired.com/story/pangram-has-emerged-as-the-gold-standard-of-ai-detection/

[7] Jonathan A. Karr Jr. et al., “Why AI Detection Fails for Academic Integrity,” arXiv:2608.11256v2; accepted to the ACM AI Leadership Summit (2026): https://arxiv.org/abs/2608.11256v2

[8] “Generative AI Floods and Dilutes the Market for Books,” arXiv:2607.20349 (2026 working paper): https://arxiv.org/abs/2607.20349

[9] Weixin Liang et al., “GPT Detectors Are Biased Against Non-Native English Writers,” *Patterns* 4(7), 2023: https://arxiv.org/abs/2304.02819

[10] Gotham Ghostwriters and Josh Bernoff, “AI and the Writing Profession” (2025): https://gothamghostwriters.com/wp-content/uploads/2025/11/AI-Writing-Survey.pdf

[11] Kate Knibbs, “More Typos, Fewer Em Dashes: Writers Are Creating an Anti-AI Literary Counterculture,” WIRED (2026): https://www.wired.com/story/more-typos-fewer-em-dashes-writers-are-creating-an-anti-ai-literary-counterculture/

[12] Vauhini Vara, “Confessions of a Viral AI Writer,” WIRED: https://www.wired.com/story/confessions-viral-ai-writer-chatgpt/
