# The Slow Lens for Hermes Agent

## What's Included

This repository now works in two modes:

- As a **Hermes Agent package**, with a portable identity plus repo-local instructions
- As a **standalone prompt pack** you can still paste into ChatGPT, Claude, or another assistant

Key files:

- **SOUL.md** -- The portable agent identity. This is the startup pitch stress tester's durable voice and reasoning style.
- **AGENTS.md** -- Repo-specific Hermes instructions. This tells Hermes how to use this repo, which files matter, and what evaluation format to default to.
- **slow-lens.md** -- The knowledge base. This captures the public, economics-first thinking behind the evaluator.
- **slow-pitch-eval.md** -- The standalone prompt export. Use this when you want the same evaluator outside Hermes.
- **IDENTITY.md / IDENTITY_SUMMARY.md / roster_entry.json** -- Companion metadata in the same style as the Hermes agent library.

## Hermes Setup

### Option 1: Use this repo as a Hermes project

Open Hermes in this directory. Hermes will pick up `AGENTS.md`, and the repo will behave like the pitch stress tester project.

### Option 2: Make this your Hermes identity

Hermes loads `SOUL.md` from `HERMES_HOME`, not from an arbitrary project folder. To make this your active Hermes persona:

1. Copy this repo's `SOUL.md` to `~/.hermes/SOUL.md`, or
2. Run Hermes with `HERMES_HOME` pointed at a directory containing this `SOUL.md`

In both cases, keep `slow-lens.md` available as the knowledge base.

## Quick Start (Hermes)

### Step 1: Start Hermes in this repo
Open Hermes with `/Users/aindaco1/Desktop/pitch-stress-tester` as the working directory.

### Step 2: Give it your pitch
Paste your deck text, memo, executive summary, or startup description into the conversation.

### Step 3: Get the stress test
The default output should cover:

- **Economics Check** -- Are the unit economics clear and defensible? What has to be true?
- **Model Check** -- Why this business model? Is there a more capital-efficient path?
- **Moat Check** -- What stops a serious competitor from replicating this?
- **Bullshit Check** -- What is vague, missing, or hand-wavy?
- **The One-Liner** -- The blunt summary a skeptical investor would use in the partner room

## Quick Start (Standalone Prompt Mode)

### Step 1: Open your AI assistant
Go to [ChatGPT](https://chat.openai.com), [Claude](https://claude.ai), or any assistant you use.

### Step 2: Start a new conversation
Paste the **entire contents** of `slow-pitch-eval.md` as your first message.

### Step 3: Add the knowledge base
Attach `slow-lens.md` as a file or paste the parts you want the assistant to rely on.

### Step 4: Feed it your pitch
Paste your deck text, memo, executive summary, or startup description.

## Tips for Getting the Most Out of It

**Be specific.** The more detail you give -- real numbers, real customers, real unit economics -- the sharper the feedback. Vague inputs get conditional output.

**Don't just pitch. Ask follow-ups.** After the initial eval, ask things like:
- "What would Will Quist push back on?"
- "Where's the weakest part of my economics argument?"
- "If you were skeptical of this, what would you say?"
- "How would you reframe my business in one sentence?"

**Run it more than once.** Try different descriptions of your business and see what changes. If the AI keeps flagging the same thing, that's probably a real gap.

**Use it before a real pitch.** This isn't a replacement for talking to investors — it's prep. Find the holes before someone else does.

## What This Is (and Isn't)

**It is:**
- A stress test based on public, economics-first venture thinking captured in `slow-lens.md`
- A way to pressure-test your pitch, business model, and assumptions
- A tool to sharpen your story before investor conversations

**It isn't:**
- Investment advice or a guarantee of anything
- A substitute for actually talking to investors
- A representation of any specific firm's private investment process
- Static — the team's thinking evolves, and we'll update these files over time

## Advanced: Persistent Hermes Use

If you want a reusable Hermes version:

1. Put the repo's `SOUL.md` where Hermes can use it as identity
2. Keep this repository as the project so `AGENTS.md` and `slow-lens.md` stay available
3. Start new evaluations inside this repo whenever you want the same voice and rubric

## Advanced: Custom GPT / Claude Project

You can still use the standalone prompt flow:

**ChatGPT:**
1. Go to [My GPTs](https://chat.openai.com/gpts/mine) -> Create a GPT
2. Paste `slow-pitch-eval.md` into the Instructions field
3. Upload `slow-lens.md` under Knowledge
4. Name it "Slow Lens" and save

**Claude:**
1. Go to [Projects](https://claude.ai) -> New Project
2. Add `slow-pitch-eval.md` as the project instructions
3. Upload `slow-lens.md` to project knowledge
4. Start a conversation within the project

---

*The Slow Lens for Hermes Agent -- Q2 2026*
*Built by Slow Ventures*
*Follow the team: [@lessin](https://x.com/lessin) · [@wquist](https://x.com/wquist) · [@yrechtman](https://x.com/yrechtman) · [@mmlightcap](https://x.com/mmlightcap) · [@slow](https://x.com/slow)*
