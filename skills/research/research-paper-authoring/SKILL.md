---
name: research-paper-authoring
description: "Use when drafting or revising scholarly research papers."
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Write research papers grounded in verifiable evidence"
  hermes:
    tags: [research, academic-writing, manuscripts, citations, reproducibility]
    related_skills: [humanizer]
---

# Research paper authoring

Write and revise scholarly manuscripts across disciplines from inspectable evidence. Adapt to the paper's genre, language, audience, and venue. This is the shared procedure for the Academic Writer and Academic Researcher profiles; it does not require either persona or an autonomous research platform.

Use for original research, reviews, theoretical work, qualitative or interpretive scholarship, and reviewer responses. For a narrow copyedit, use `humanizer` directly with its academic preservation mode. Keep the scope proportional: editing one paragraph does not require rebuilding a whole research project.

## Establish the paper's actual state

Read the available project brief, draft, bibliography, research notes, datasets, analysis code, results, and prior reviews. Ask only for missing decisions that change the work: research question, paper type, target venue, available evidence, intended contribution, and output format. An unspecified venue need not block a working draft; identify formatting assumptions.

Separate these states explicitly:

- **Proposal or protocol:** planned methods and expected outcomes, never reported as completed research.
- **Evidence-backed draft:** claims trace to inspected sources, supplied observations, proofs, or executed analyses. Mark which results are supplied by the author and which you reproduced.
- **Incomplete draft:** useful supported sections plus conspicuous evidence gaps. Do not fill missing results, quotations, references, approvals, or author details with plausible inventions.

Simulation and synthetic data can be legitimate research when their generation, assumptions, and limitations are disclosed. Never present them as empirical observations or independent validation.

## Build the evidence before the narrative

1. **Define the contribution as a question and a bounded answer.** Search for the closest prior work and credible contrary findings before claiming novelty. A search that finds no match does not prove priority.
2. **Check current venue requirements when a venue is named.** Read its official author instructions, paper-type requirements, citation style, review anonymity, AI-use/disclosure policy, and relevant reporting standard. Record the URL and date. Requirements differ by venue and discipline; do not invent a universal preprint quota, section structure, or AI policy.
3. **Verify sources in two separate senses.** Confirm bibliographic identity against an authoritative record, then inspect the passage, table, figure, or argument supporting the claim. A resolving DOI or a real title proves existence, not entailment. Import citation metadata from the verified record; do not generate it from memory. For books, archives, and non-DOI materials, record edition, stable catalogue/archive identifier, and locator.
4. **Track access and status.** Distinguish full text read, abstract only, metadata only, and unavailable. Label preprints, peer-reviewed work, datasets, primary documents, and vendor claims. Check for a version of record, corrections, retractions, and substantive critiques. Do not silently replace a preprint if the relevant finding changed in publication. A PubPeer comment is a lead to investigate, not a verdict.
5. **Map central claims to evidence.** Use the compact templates in [references/evidence-records.md](references/evidence-records.md) when a manuscript needs an audit trail. Keep qualifiers, populations, denominators, time periods, source versions, uncertainty, and contradictions attached to each claim. Do not cite a paper's reference list as if you read the underlying studies.

If full text is unavailable, narrow the claim to what you actually inspected or mark it for verification. Continue supported work; never convert an access failure into a fabricated citation or confident summary. Use existing authorized repositories and connectors before requesting material the project already holds.

## Match the argument to the research

Read [references/paper-types.md](references/paper-types.md) for the applicable genre. Empirical papers often benefit from methods/results first and abstract last; interpretive and theoretical papers may need a different structure. Follow the actual argument and venue.

- Report what was done, including deviations, failed checks, null results, exclusions, and limitations that affect the conclusion. Separate observations from interpretation and exploratory findings from prespecified tests.
- For quantitative work, reconcile denominators, units, effect estimates, intervals, sample sizes, comparisons, and assumptions with the underlying outputs. Statistical significance alone does not establish importance or causality. Do not add a test, confidence interval, or replication claim that was never performed.
- For computational work, retain data versions, code revision, environment, commands, seeds where relevant, configuration, logs, and outputs. Inspect the implementation and underlying data; a clean exit code or a model-generated reviewer score does not validate the science.
- For qualitative and historical work, retain source locators, selection rationale, transcription/translation choices, coding or interpretive decisions, and contrary cases. Do not invent participant voices or imply consent/access that has not been documented.
- For theoretical work, state assumptions and delimit proven results, conjectures, examples, and numerical checks. Flag proof gaps instead of smoothing them into assertions.

Writing a paper does not by itself authorize new data collection, paid compute, external uploads, or submission. Execute additional research only within the user's scope and applicable requirements; otherwise produce the needed protocol or identify the missing evidence. Do not install or run the systems discussed in the source notes merely because they are mentioned there.

## Review tables, figures, and equations as evidence

Create quantitative plots from actual analysis outputs with reproducible plotting tools. Keep illustrative schematics distinct from measured results. Check every label, legend, caption, axis, unit, uncertainty interval, panel, and in-text reference against the source data or intended mechanism. Render the final document and inspect figures at reading size; text-only review misses visual errors. If rendering is unavailable, report that visual verification remains open.

Check notation and equation consistency, including definitions and assumptions. Do not decorate scientific figures with generated imagery that implies observations or mechanisms unsupported by the work. Follow the venue's image rules for any illustrative AI content.

## Required humanizer pass

Before delivering newly drafted or substantially revised manuscript prose, load the existing **`humanizer`** skill and select **Research and academic writing** mode, including its `references/academic-writing-audit.md`. Use the runtime's skill loader or discovered skill path; do not assume the two packages are siblings in both runtimes. In this repository its source is `skills/creative/humanizer/`.

Give the humanizer the prose plus its preservation anchors: claims, qualifications, technical vocabulary, quotations, citation keys and locators, equations, numbers, and disclosure text. It may remove inflated framing, unnecessary acronym density, repetition, and mechanical transitions. It must preserve justified uncertainty and the author's disciplinary voice. It must not add anecdotes, manufacture originality, disguise AI provenance, or optimize a detector score.

Then compare the edited version against the evidence map and original anchors. Revert semantic drift; route factual problems back to verification. If `humanizer` is unavailable, identify the missing dependency, keep drafting and evidence work moving, and report the editorial pass as incomplete instead of claiming it ran.

## Final review and handoff

Do one focused challenge pass: what evidence would disconfirm the main conclusion, what is the strongest alternative explanation, and can a reader retrace the reasoning? An AI critique is editorial assistance, not independent peer review. Request domain review for unresolved substantive issues; do not claim expertise, reproducibility, or acceptance that has not been demonstrated.

For a full manuscript, deliver the requested editable draft and bibliography, with concise notes on verified evidence, remaining gaps, reproducibility/visual checks actually performed, and AI assistance. Use existing project records rather than making redundant files. For reviewer responses, map each comment to the change and its location or give an evidence-based explanation for disagreement; never claim unperformed experiments.

Keep an accurate AI-use record: tools/models and versions if known, dates, tasks, affected sections/assets, and human verification. Draft disclosure from that record using the venue's current policy, preserving author accountability. Do not list AI as a human author or strip disclosure during humanization. Resolve unsupported central claims before labeling the package ready for author submission review. Submission remains a separate authorized action.

## Background and source limits

[references/source-notes.md](references/source-notes.md) records the IEEE Spectrum investigation, its linked research and systems, methodological caveats, and supplementary official guidance. Read it when explaining the rationale, assessing AI-research claims, or updating this procedure. It is a dated evidence map, not a substitute for fresh topic-specific research or current venue instructions.
