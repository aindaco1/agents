# Pangram methodology and evidence audit (reviewed 2026-08-07)

Use this note when interpreting Pangram results, evaluating claims about Pangram, or planning detector-aware editorial work. Re-check live model cards and papers before quoting numbers: detector versions and operating thresholds change.

## Evidence classes

1. **First-party methodology/performance:** Pangram model cards, technical reports, and research pages. These establish what the vendor says the model does, its intended scope, definitions, thresholds, and internal results. They do not independently validate the product.
2. **Vendor summaries of external studies:** Pangram’s “third-party evals” blog is a discovery aid, not independent evidence by itself. Follow every claim to the underlying paper and preserve its detector version, sample, metric, threshold, and condition.
3. **Externally run evaluations:** Give these more weight, but check API credits, author relationships, publication status, threshold selection, train/test overlap, and whether the tested Pangram version is still current.
4. **Anecdotal scans:** Useful only for generating hypotheses about one exact input and service state. They do not establish a general writing rule.

## Current first-party claims and scope

Sources:

- Model card: https://www.pangram.com/research/model-card/pangram-4
- Technical report: https://pangram-public.s3.us-east-1.amazonaws.com/pdf/pangram_4_technical_report.pdf
- Overview: https://www.pangram.com/research/how-it-works
- Original Pangram report: https://arxiv.org/abs/2402.14873

Pangram 4 uses a sparse mixture-of-experts language-model backbone with segment, token-provenance, mixed-authorship, and humanizer heads. It processes overlapping 512-token windows and combines token- and segment-level evidence with calibrated structured decoding. Product boundaries are smoothed to roughly two-sentence minimum segments.

Training combines licensed human prose with in-house synthetic “mirrors” on matched topics. AI-assisted examples are produced by applying AI edits to human documents; lexical and semantic alignment supplies synthetic Human, AI-Assisted, and AI-Generated labels. A hard-negative mining stage adds human texts that an earlier checkpoint mislabeled.

Operational definitions matter:

- Input must be at least 50 words of complete-sentence natural-language prose.
- Short replies, one-answer factual responses, code, references, tables of contents, manuals, templated/automated writing, and math-dominated text are outside primary scope or more error-prone.
- Light copyediting, literal translation, spelling, and grammar fixes are intended to remain Human.
- A document is labeled Human at ≥90% human-classified characters, AI at ≥80% AI-generated characters, and Mixed otherwise. Mixed is therefore partly a thresholded residual category, not proof of one specific collaboration process.
- `ai_assistance_score` is not the probability that the displayed label is correct. Segment confidence is posterior peakedness, not calibrated correctness.
- Raw text or DOCX is preferred over PDF because extraction artifacts can alter the input.

Pangram reports an internal English false-positive rate of 0.0041% (41/1,000,000 FineWeb examples) and a false-negative rate of 0.3396% (1,766/519,993 generations from 26 model variants). Treat both as large first-party tests, not portable guarantees for every editorial corpus. The same report shows the harder mixed-authorship problem is not solved: “Mixed” recall was 55.01% on 14,990 substantially edited student texts and 65.17% on 4,826 WildChat-derived edits.

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
- Paper: *People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text* (Russell, Karpinska, Iyyer), ACL 2025.
- Corpus: 300 American-English nonfiction articles under 1,000 words, organized into five 60-article experiments, with human articles from eight US publications and AI articles from GPT-4o, Claude 3.5 Sonnet, paraphrased GPT-4o, o1-Pro, and humanized o1-Pro.
- Pangram Humanizers result: overall TPR 99.3% with FPR 2.7%. Pangram base: overall TPR 98.0% with FPR 2.0%. These are **TPR/FPR pairs, not “99.3% accuracy.”**
- Hardest reported condition, humanized o1-Pro: Pangram Humanizers TPR 96.7% / FPR 10.0%; Pangram base TPR 96.7% / FPR 6.7%. Each condition contained only 30 human and 30 AI articles, so condition-level percentages are coarse.
- Threshold handling: researchers used Pangram API labels and did not award credit for the neutral “Possibly AI” label.
- Scope/disclosures: the study is about expert human detection, not a dedicated Pangram audit. It thanks Pangram and GPTZero for API credits. Its first author later appears among the Pangram 4 report authors, so describe it as an external academic evaluation with disclosed product access—not unqualified fully independent validation.
- Editorial inference: strong evidence that the tested Pangram configurations performed well on this narrow article benchmark, but humanization-specific FPR can be materially higher than the aggregate. The paper itself favors explainable human review for high-stakes decisions.

### Higher-education comparison

- DOI: https://doi.org/10.1007/s40979-026-00226-w
- The study compares GPTZero, Pangram, Copyleaks, and Turnitin on fully human, fully AI, hybrid, and humanized academic papers.
- Before quoting a Pangram percentage from this source, recover the exact row, paper type, threshold, sample size, and detector version. Do not collapse fully generated, hybrid, and humanized conditions into one “accuracy” number.

## Failure modes to carry into editing

- **Version drift:** evidence for API v2025-05 or Pangram 3 does not automatically validate Pangram 4, and vice versa.
- **Domain and input drift:** headline error rates do not transfer automatically to poetry, scripts, manuals, references, code, math, very short text, OCR-corrupted PDFs, or a publication’s distinctive house style.
- **Context dependence:** isolated spans can score differently in the full document. Do not interpret model-smoothed segment boundaries as exact provenance boundaries.
- **Hybrid ambiguity:** a Mixed label cannot reconstruct who supplied ideas, wording, research, prompts, or final decisions. Mixed recall is also notably lower than binary full-generation performance.
- **Adversarial false negatives:** paraphrasing and humanizers can reduce detection; robustness depends on the attack family and version. Passing after rewriting is not evidence of human authorship.
- **Cascading humanizer blind spot:** the auxiliary humanizer head runs only when the primary detector first finds AI evidence, so an absent humanizer flag is not an independent clearance.
- **False positives:** even a low measured FPR is not zero and does not equal the posterior probability of misconduct. Base prevalence, domain shift, and consequences matter.
- **Non-native writing:** Pangram reports low internal FPR on several learner-English corpora, but that does not eliminate individual error or validate every language/register. Never infer native status, intent, or dishonesty from a score.
- **Opaque causality:** a flagged span does not reveal which word, cadence, or editorial feature caused the label. Do not derive universal “AI tells” from one report.

## Editorial rules

1. Use Pangram for **triage**, not verdicts.
2. Preserve the exact submitted text and record model/version, date, input scope, preprocessing, labels, fractions, confidence, and humanizer output.
3. Re-run only on documented in-scope prose, preferably the full clean document. Keep an untouched master.
4. Seek process evidence: drafts, notes, tracked changes, source files, research trail, and an author explanation.
5. Give the author notice, a chance to respond, and an appeal/correction route before consequential action.
6. Align consequences with the actual policy. Detection of assistance is not proof that prohibited assistance occurred.
7. Do not edit toward a Human label by injecting errors or stereotyped “human” style. Restore the author’s own language and substantive choices instead.
8. If genuine material AI rewriting occurred, an AI-Assisted/Mixed result may be accurate; score-chasing would conceal rather than clarify provenance.
9. Never describe a detector score as proof, authorship probability, plagiarism finding, factuality check, or intent assessment.
