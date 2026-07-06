# Ethical OS Toolkit — working reference

Source: `/Users/aindaco1/Desktop/Ethical OS Toolkit.pdf`
Extracted full text: `/Users/aindaco1/.hermes/references/ethical-os-toolkit-extract.md`
License noted in source: CC BY-NC-SA 4.0, Institute for the Future + Omidyar Network, 2018.

## Core use

Use the toolkit to anticipate second- and third-order social harms from technology before build, launch, scale, or public deployment. It is not a compliance checklist. It is a foresight and mitigation workflow.

Default sequence:
1. Describe the technology, user groups, affected non-users, business model, data flows, and likely scaling path.
2. Run the eight risk zones below.
3. Pick the 2-3 highest-risk zones by severity, likelihood, reversibility, and who bears the harm.
4. Run at least one risky-future scenario or pre-mortem for each priority zone.
5. Convert findings into design, governance, business-model, moderation, monitoring, and rollback decisions.
6. Name owners, trigger points, and review cadence.

## The 8 Ethical OS risk zones

1. Truth, disinformation, and propaganda
   - Could bad actors use the product to attack shared facts, impersonate people, produce misleading media, automate manipulation, or launder propaganda?
   - What data, claims, scores, or outputs will users treat as authoritative?

2. Addiction and the dopamine economy
   - Does the business model reward maximizing attention, engagement, compulsion, or emotional dependency?
   - What harms appear if the product becomes habit-forming among minors, isolated users, patients, workers, or politically vulnerable groups?

3. Economic and asset inequalities
   - Who gets access and who is excluded?
   - Does the product concentrate wealth, power, visibility, opportunity, or bargaining leverage?
   - What happens to workers, creators, local communities, and people outside the target market?

4. Machine ethics and algorithmic bias
   - Does the system use ML, automated scoring, ranking, recommendations, or decision support?
   - Are training data, labels, objectives, proxies, or feedback loops biased?
   - Who is harmed by false positives, false negatives, opacity, or automation bias?

5. Surveillance state
   - Could governments, police, militaries, employers, schools, landlords, abusers, or platforms use the system for monitoring, chilling speech, exclusion, or repression?
   - What becomes dangerous if combined with facial recognition, location data, biometrics, metadata, or social graphs?

6. Data control and monetization
   - What data is collected, inferred, retained, sold, shared, or used for targeting?
   - Is data collection necessary and legible to users?
   - Can users access, correct, export, delete, or refuse data collection without losing essential access?

7. Implicit trust and user understanding
   - Do users understand what the system can do, cannot do, and is optimizing for?
   - Are terms, model limits, failure modes, sponsored content, automated decisions, and data practices visible in plain language?
   - Is there a usable non-extractive or lower-data alternative?

8. Hateful and criminal actors
   - How could the product enable harassment, stalking, fraud, theft, ransomware, extremist organizing, doxxing, exploitation, or violence?
   - What abuse patterns emerge at scale, and what enforcement, reporting, friction, and response capacity exists?

## Future-proofing strategies from the toolkit

Use these as mitigation patterns, not slogans:

1. Tech ethics literacy
   - Build ethical risk review into design, engineering, product, and governance education.

2. Data-worker oath / professional commitment
   - Make duties to affected people explicit: minimize harm, respect agency, communicate limits, and refuse unsafe use.

3. Ethical bounty hunters
   - Invite external reviewers, researchers, workers, users, and affected communities to find social risks before they become incidents. Reward them.

4. Red flag rules
   - Define launch blockers and escalation triggers: vulnerable population impact, opaque automated decisions, irreversible data collection, abuse patterns, misleading claims, coercive consent, or surveillance use.

5. Healthy platforms
   - Track public-interest metrics, not only growth: user well-being, abuse prevalence, moderation latency, misinformation spread, concentration of reach, creator/community health, opt-out rates, appeal outcomes.

6. License to design / accountable practice
   - Treat high-impact technology design as a public responsibility. Require review, documentation, accountability, and consequences for reckless deployment.

## Minimal output format for reviews

When using this toolkit, return:

1. System being reviewed: one paragraph.
2. Top risk zones: ranked list with why each matters.
3. Who bears the harm: users, non-users, workers, communities, public institutions.
4. Worst plausible misuse or failure: scenario, not abstract category.
5. Existing safeguards: what already reduces risk.
6. Missing safeguards: what is absent.
7. Mitigation plan: concrete design/product/policy/ops changes.
8. Red flags: conditions that should block launch or trigger rollback.
9. Open questions: what must be learned from users, affected communities, legal, security, or research.

## Political/material lens

Do not reduce ethical review to brand risk, reputational exposure, or legal compliance. Ask who gains power, who loses agency, who becomes data, who gets surveilled, who is excluded, who has recourse, and whether the system strengthens or weakens collective capacity.
