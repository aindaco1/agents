# Pangram methodology and evidence audit (reviewed 2026-09-05)

Use this note when interpreting Pangram results, evaluating claims about Pangram, or planning detector-aware editorial work. Re-check live model cards and papers before quoting numbers: detector versions and operating thresholds change. The August-dated filename is retained to avoid breaking existing references.

## Evidence classes

1. **First-party methodology/performance:** Pangram model cards, technical reports, and research pages. These establish what the vendor says the model does, its intended scope, definitions, thresholds, and internal results. They do not independently validate the product.
2. **Vendor summaries of external studies:** Pangram’s “third-party evals” blog is a discovery aid, not independent evidence by itself. Follow every claim to the underlying paper and preserve its detector version, sample, metric, threshold, and condition.
3. **Externally run evaluations:** Give these more weight, but check API credits, author relationships, publication status, threshold selection, train/test overlap, and whether the tested Pangram version is still current.
4. **Journalism and public case reports:** Use these to understand deployment, incentives, harms, and disclosed relationships. A reported scan or public accusation is not a controlled validation study.
5. **Anecdotal scans:** Useful only for generating hypotheses about one exact input and service state. They do not establish a general writing rule.

## Current first-party claims and scope

Sources:

- Model card: https://www.pangram.com/research/model-card/pangram-4
- Technical report: https://pangram-public.s3.us-east-1.amazonaws.com/pdf/pangram_4_technical_report.pdf
- Overview: https://www.pangram.com/research/how-it-works
- Original Pangram report: https://arxiv.org/abs/2402.14873

Pangram 4 uses a sparse mixture-of-experts language-model backbone with segment, token-provenance, mixed-authorship, and humanizer heads. It processes overlapping 512-token windows and combines token- and segment-level evidence with calibrated structured decoding. Product boundaries are smoothed to roughly two-sentence minimum segments.

Training combines licensed human prose with in-house synthetic “mirrors” on matched topics. AI-assisted examples are produced by applying AI edits to human documents; lexical and semantic alignment supplies synthetic Human, AI-Assisted, and AI-Generated labels. A hard-negative mining stage adds human texts that an earlier checkpoint mislabeled.

Operational definitions matter:

- Input must be at least 50 words of complete-sentence natural-language prose. This is a hard floor, not a guarantee that a 50-word excerpt carries enough evidence for a consequential judgment. WIRED reports that Pangram acknowledges weaker performance below 100 words; prefer at least 100 words and the full prose context when available.
- Short replies, one-answer factual responses, code, references, tables of contents, manuals, templated/automated writing, and math-dominated text are outside primary scope or more error-prone.
- Light copyediting, literal translation, spelling, and grammar fixes are intended to remain Human.
- A document is labeled Human at ≥90% human-classified characters, AI at ≥80% AI-generated characters, and Mixed otherwise. Mixed is therefore partly a thresholded residual category, not proof of one specific collaboration process.
- `ai_assistance_score` is not the probability that the displayed label is correct. Segment confidence is posterior peakedness, not calibrated correctness.
- Raw text or DOCX is preferred over PDF because extraction artifacts can alter the input.

Pangram reports an internal English false-positive rate of 0.0041% (41/1,000,000 FineWeb examples) and a false-negative rate of 0.3396% (1,766/519,993 generations from 26 model variants). Treat both as large first-party tests, not portable guarantees for every editorial corpus. The same report shows the harder mixed-authorship problem is not solved: “Mixed” recall was 55.01% on 14,990 substantially edited student texts and 65.17% on 4,826 WildChat-derived edits. On the 14,990-text editing set, Pangram 4 still labeled 41.37% Human, 55.01% Mixed, and 3.62% AI.

Pangram’s own limitations section says errors occur, decisions are partly black-box, the same passage can receive a different prediction in isolation versus full-document context, and human style may drift toward LLM-like style over time.

## External evidence reviewed

### UChicago/Becker Friedman Institute working paper

- Landing page: https://bfi.uchicago.edu/working-papers/artificial-writing-and-automated-detection/
- Paper title: *Artificial Writing and Automated Detection* (Jabarian and Imas), version dated 2025-08-26.
- Tested **Pangram API v2025-05**, not Pangram 4.
- Corpus: 1,992 pre-2020 human passages across news, blogs, Amazon reviews, Yelp restaurant reviews, novels, and résumés. Each human corpus was matched with AI generations from GPT-4.1, Claude Opus 4, Claude Sonnet 4, and Gemini 2.0 Flash.
- Main claim: Pangram had near-zero FPR/FNR within this stimulus set, remained relatively strong on under-50-word “stubs,” and resisted StealthGPT’s default rewrite better than comparators.
- Important conditions: genre-specific “optimal” thresholds were selected by maximizing Youden’s J on the evaluated corpus; the paper also reports raw-threshold sensitivity and policy-cap analyses. The paper does not report an independent check for overlap between public human corpora and Pangram’s proprietary training data.
- Editorial inference: this is meaningful positive external evidence for the May 2025 service on those six genres and generators. It does not validate Pangram 4 below its documented 50-word minimum, mixed-authorship attribution, or every editorial domain. Optimized-on-evaluation-corpus figures should not be treated as untouched holdout deployment estimates.
- Disclosure: authors reported no financial or personal conflict; funding included University of Chicago programs and Google Cloud Research.

### ACL 2025 / UMass human-detector study

- arXiv: https://arxiv.org/abs/2501.15654
- Paper: *People Who Frequently Use ChatGPT for Writing Tasks Are Accurate and Robust Detectors of AI-Generated Text* (Russell, Karpinska, Iyyer), ACL 2025.
- Corpus: 300 American-English nonfiction articles under 1,000 words, organized into five 60-article experiments, with human articles from eight US publications and AI articles from GPT-4o, Claude 3.5 Sonnet, paraphrased GPT-4o, o1-Pro, and humanized o1-Pro.
- Pangram Humanizers result: overall TPR 99.3% with FPR 2.7%. Pangram base: overall TPR 98.0% with FPR 2.0%. These are **TPR/FPR pairs, not “99.3% accuracy.”**
- Hardest reported condition, humanized o1-Pro: Pangram Humanizers TPR 96.7% / FPR 10.0%; Pangram base TPR 96.7% / FPR 6.7%. Each condition contained only 30 human and 30 AI articles, so condition-level percentages are coarse.
- Threshold handling: researchers used Pangram API labels and did not award credit for the neutral “Possibly AI” label.
- Scope/disclosures: the study is about expert human detection, not a dedicated Pangram audit. It thanks Pangram and GPTZero for API credits. Its first author later appears among the Pangram 4 report authors, so describe it as an external academic evaluation with disclosed product access—not unqualified fully independent validation.
- Editorial inference: strong evidence that the tested Pangram configurations performed well on this narrow article benchmark, but humanization-specific FPR can be materially higher than the aggregate. The paper itself favors explainable human review for high-stakes decisions.

### Notre Dame academic-integrity preprint

- Versioned paper: https://arxiv.org/abs/2608.11256v2
- Paper: *Why AI Detection Fails for Academic Integrity*, submitted 2026-08-06 and revised 2026-08-20. The arXiv record says it was accepted to the ACM AI Leadership Summit; use v2 rather than the superseded v1, and note that the posted PDF still contains placeholder ISBN/DOI fields.
- Corpus: 642 English-language published abstracts, 25–500 words, from chemistry, computer science, political science, and theology. The authors split them between 2013–2015 and 2023–2025, then produced three Gemini 3 Flash rewrite conditions and scanned with **Pangram 3.2** and GPTZero at a 0.5 cutoff.
- Original-text result: Pangram flagged 0% of 306 pre-LLM-era originals, but 15.0% of 336 originals from 2023–2025. The authors correctly call the latter a *flag rate*, not a confirmed false-positive rate, because AI assistance in those recent publications is unknown. Domain rates varied sharply: 2.1% for chemistry and 26.6% for theology in the recent set.
- Light-edit result: Pangram flagged 64.4% of “refine abstract only” edits in the older set and 80.1% in the recent set. This demonstrates that detector output cannot by itself distinguish policy-permitted editing from policy-forbidden generation. It does **not** mean those LLM-edited outputs were detector false positives under Pangram’s own mixed-authorship definition.
- Evasion result: after all rewrite conditions passed through Undetectable AI v11, Pangram’s false-negative rate was 98.5% for the older set and 96.6% for the newer set—fewer than 4% remained detected. This is strong evidence against assuming all commercial humanizers fail, but it is one attack service, one generator, a preprint setup, and an older Pangram version.
- Disclosure: the acknowledgments thank Pangram for API use, along with Notre Dame Teaching & Learning and the Notre Dame AI Council. The v2 PDF contains no separate conflict-of-interest or funding statement.
- Editorial inference: do not convert Pangram 3.2 results into Pangram 4 claims. More importantly, detector-aware editing must not become evasion: a pass after humanization is not evidence of human authorship, and a flag after light editing is not proof that the human supplied no ideas or original draft.

### 14,419-book self-published-fiction preprint

- Preprint: https://arxiv.org/abs/2607.20349
- Paper: *Generative AI Floods and Dilutes the Market for Books* (2026 working paper).
- Corpus: 14,419 genre-fiction ebooks released from January 2023 through March 2026 and observed through a proprietary Amazon sales panel. Eligibility excluded titles whose sales rank never fell below 1.5 million, so this is not a prevalence estimate for every self-published book.
- Detector method: researchers removed front/back matter, scanned full chapters with **Pangram 3.3**, then defined a book score as the percentage of detector windows whose label was not “Human Written.” “No AI text” meant 0%; “light AI text” meant >0% and ≤25%; “substantial AI text” meant >25%.
- Result: 20.0% of the sample fell into the study’s detector-defined “substantial AI text” band, 17.1% into “light,” and 62.9% into “no AI.” Say “Pangram 3.3 placed 20% in the >25%-flagged-windows band,” not “20% were proven AI-written.”
- Exact band counts in the paper-linked anonymized data are 2,880 substantial, 2,471 light, and 9,068 no-AI out of 14,419.
- Scope: the paper’s market-dilution comparisons are observational; the authors say genre comparisons can differ along many unobserved dimensions. Its detector strata cannot independently establish the writing history of any named book.
- Relationship disclosure from WIRED: lead author Tuhin Chakrabarty said Pangram founder Max Spero supplied API credits, continued supporting the research, and became a close friend. WIRED also reported that Chakrabarty’s partner, literary agent Todd Shuster, consults for Pangram and makes publisher introductions. These facts do not invalidate the work, but they matter when describing it as “independent” or using it to validate the vendor.

### 2023 non-native-English bias study

- Paper: Weixin Liang et al., *GPT Detectors Are Biased Against Non-Native English Writers*: https://arxiv.org/abs/2304.02819
- Corpus: 91 TOEFL essays from a Chinese educational forum and 88 US eighth-grade essays, tested with seven public detectors available in 2023.
- Result: the mean false-positive rate across detectors was 61.22% on the TOEFL essays; all seven flagged 18/91, and at least one flagged 89/91. Detector results tracked lower perplexity and narrower lexical variation.
- Limits: the sample was small, most tested systems used GPT-2 backbones, and the authors explicitly call for broader testing. The paper predates Pangram and cannot be cited as evidence that Pangram 3 or 4 shares the measured error rates.
- Editorial inference: use the study as a fairness warning, not a current-product verdict. Never “fix” a non-native register by stereotyping, injecting errors, or forcing ornate vocabulary. Require per-domain validation and process evidence before imposing consequences.

### Higher-education comparison

- DOI: https://doi.org/10.1007/s40979-026-00226-w
- The study compares GPTZero, Pangram, Copyleaks, and Turnitin on fully human, fully AI, hybrid, and humanized academic papers.
- Before quoting a Pangram percentage from this source, recover the exact row, paper type, threshold, sample size, and detector version. Do not collapse fully generated, hybrid, and humanized conditions into one “accuracy” number.

## Context, incentives, and deployment reporting

### WIRED’s Pangram profile

- Article: Lexi Pandell, “Pangram Has Emerged as the Gold Standard of AI Detection,” WIRED, 2026-09-02: https://www.wired.com/story/pangram-has-emerged-as-the-gold-standard-of-ai-detection/
- Evidence type: reported profile, not a controlled model evaluation. The title describes market reputation; it is not a scientific designation.
- Useful findings: Pangram is increasingly used by platforms, publishers, agents, and educators; short excerpts and public callouts can carry severe reputational consequences; and the people deciding whose work to scan or accuse introduce a separate selection-bias problem even if the model’s benchmark error rate is low.
- Product disclosures reported by WIRED: performance worsens below 100 words; the median submitted input was about 350 words; an identical passage can receive different verdicts alone versus in context; and the vendor’s conservative operating point trades fewer false positives for more AI text missed.
- Governance implication: follow the approach WIRED quotes from Penguin Random House—use detection only as one non-determinative input in a broader editorial process. Do not post allegations, cancel work, penalize a student, or terminate a relationship from a detector result alone. Preserve the input, seek drafts/version history, notify the author, allow a response, and provide an appeal or correction route.
- Fairness implication: the three publishing scandals discussed in the article involved writers of color, while the 2023 detector-bias study did not test Pangram. That pattern is a reason to audit selection and consequences, not statistical proof of Pangram bias. Claims from neurodivergent writers are also reported testimony, not yet a quantified Pangram evaluation.
- Incentive implication: disclose API credits, consulting, referral, promotional, friendship, and publication relationships when characterizing a study or public scan. Do not let a vendor’s social-media amplification substitute for independent replication.

### Gotham Ghostwriters survey cited by WIRED

- Report: *AI and the Writing Profession* (Gotham Ghostwriters and Josh Bernoff, 2025): https://gothamghostwriters.com/wp-content/uploads/2025/11/AI-Writing-Survey.pdf
- Sample: 1,481 completed responses, split into 1,190 writing professionals and 291 fiction authors. It was a sponsor-recruited **non-probability online survey**, fielded in August–September 2025; it is descriptive of respondents, not a population prevalence study.
- Correct denominator: 61% of the 1,190 writing professionals said they used AI at least sometimes. Among writing-professional AI users, 7% said they generated text for publication without significant editing. Do not state that 7% of all 1,481 respondents published AI-generated text.
- Fiction authors were analyzed separately: 42% of 291 used AI at least sometimes. The report says 11% of fiction-author AI users used AI weekly to create publishable text.
- Editorial inference: “AI use” covers search, brainstorming, titles, word-finding, research, outlining, editing, and generation. It is not a usable base rate for undeclared full-text generation and cannot turn a detector score into a posterior probability of misconduct.

### Pangram’s prize-fiction scans

- Vendor post: https://www.pangram.com/blog/ai-is-writing-prize-winning-fiction
- Treat claims about prize entries as Pangram-run case studies, not independent prevalence estimates. The post discloses that author Jenna Russell was completing a PhD internship as a Pangram research scientist. The company chose the corpus, detector, version, and publication framing; the detector labels are not verified writing histories.
- Preserve score semantics: the post defines its percentage as the fraction of detector segments classified as AI. That is not a word fraction, calibrated authorship probability, or proof of a writer’s process.
- Editorial inference: use such posts to identify hypotheses or documents for follow-up. Do not use them to claim a named writer used AI without corroborating process evidence and a chance to respond.

### Cited reporting on source files, counterstyle, and writing process

- Drey Dossier video cited by WIRED: https://www.youtube.com/watch?v=tv_3L_1avKM
  - The publicly circulated *Shy Girl* scan contained an `oceanofpdf.com` marker. WIRED separately reports that Max Spero put that pirated PDF directly into Pangram without reading the whole file first.
  - This supports authenticating the edition and recording PDF extraction, OCR, conversion, and preprocessing. It does **not** prove that those artifacts changed the score; that causal claim was not tested.
- WIRED on anti-AI literary counterculture: https://www.wired.com/story/more-typos-fewer-em-dashes-writers-are-creating-an-anti-ai-literary-counterculture/
  - Writers report avoiding legitimate punctuation and keeping mistakes to signal humanness. These are reported experiences, not controlled detector findings.
  - Never turn em dashes, triplets, polished grammar, passive voice, or any other isolated convention into a blacklist. A cosmetic counterstyle can be imitated too; the target remains good, faithful writing.
- WIRED, “Confessions of a Viral AI Writer”: https://www.wired.com/story/confessions-viral-ai-writer-chatgpt/
  - This first-person process account is not a detector study. It shows why repeated “less clichéd” prompting can merely exchange one stock phrase for another and why apparently intimate prose cannot prove human provenance.
  - Stop recursive model polishing. Return to the writer’s drafts, observations, objections, and choices; accept truthful mixed provenance when substantial model prose remains.

## Failure modes to carry into editing

- **Version drift:** evidence for API v2025-05, Pangram 3.2, or Pangram 3.3 does not automatically validate Pangram 4, and vice versa.
- **Domain and input drift:** headline error rates do not transfer automatically to poetry, scripts, manuals, references, code, math, very short text, OCR-corrupted PDFs, or a publication’s distinctive house style.
- **Short-text overreach:** Pangram’s 50-word minimum is a floor. Prefer ≥100 words and full context; do not compare a short excerpt’s result with a full-document result as if scope were unchanged.
- **Context dependence:** isolated spans can score differently in the full document. Do not interpret model-smoothed segment boundaries as exact provenance boundaries.
- **Hybrid ambiguity:** a Mixed label cannot reconstruct who supplied ideas, wording, research, prompts, or final decisions. Mixed recall is also notably lower than binary full-generation performance.
- **Adversarial false negatives:** paraphrasing and humanizers can reduce detection; robustness depends on attack family and version. Passing after rewriting is not evidence of human authorship.
- **Cascading humanizer blind spot:** the auxiliary humanizer head runs only when the primary detector first finds AI evidence, so an absent humanizer flag is not an independent clearance.
- **False positives:** even a low measured FPR is not zero and does not equal the posterior probability of misconduct. Base prevalence, domain shift, and consequences matter.
- **Fairness and selection:** older detectors showed severe errors on one non-native-English corpus, while current Pangram claims lower internal error on learner-English sets. Neither fact settles current fairness across domains. Also audit who gets scanned, who gets believed, and who bears the cost of appeal.
- **Opaque causality:** a flagged span does not reveal which word, cadence, or editorial feature caused the label. Do not derive universal “AI tells” from one report.
- **Institutional laundering:** calling a tool a “gold standard,” listing customers, or citing vendor-amplified studies does not convert output into proof.

## Editorial and due-process rules

1. Use Pangram for **triage**, not verdicts.
2. Authenticate and preserve the exact edition or source file. Record model/version, date, input scope, PDF extraction/OCR/conversion, other preprocessing, labels, fractions, confidence, and humanizer output.
3. Re-run only on documented in-scope prose, preferably at least 100 words and in the full clean document. Keep an untouched master and do not mix short-excerpt results with full-context results.
4. Seek process evidence: drafts, notes, tracked changes, source files, research trail, and an author explanation.
5. Give the author notice, the exact evidence, a chance to respond, and an appeal/correction route before consequential action.
6. Audit selective enforcement. Record why this text was scanned and compare the rule with how peers are treated.
7. Align consequences with the actual policy. Detection of assistance is not proof that prohibited assistance occurred.
8. Do not edit toward a Human label by injecting errors, flattening non-native or neurodivergent expression, or manufacturing stereotyped “human” style. Restore the author’s own language and substantive choices instead.
9. If genuine material AI rewriting occurred, an AI-Assisted/Mixed result may be accurate; score-chasing would conceal rather than clarify provenance.
10. Never describe a detector score as proof, authorship probability, plagiarism finding, factuality check, intent assessment, or a reconstruction of the writing process.
11. Before uploading student work, confidential manuscripts, or unpublished material to a third-party detector, confirm authorization, retention/privacy terms, and applicable FERPA, GDPR, contractual, or institutional rules.
