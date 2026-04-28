# Model Recommendation Framework

## Provider Lineups (as of Apr 18, 2026)

### Anthropic
- **Claude Sonnet 4.6** — Best default for most work. Near-Opus quality on many real-world agent, coding, and knowledge tasks at Sonnet pricing.
- **Claude Opus 4.5** — Maximum reasoning power for the hardest long-horizon analysis, architecture, and agent orchestration work.
- **Claude Haiku 4.5** — Fastest and cheapest Claude tier. Good for high-volume structured work and lightweight assistants.

### OpenAI
- **GPT-5.4** — Current flagship for complex reasoning, coding, multimodal work, and long-horizon agent workflows.
- **GPT-5.4 mini** — Strongest mini model yet. Best balance for coding, subagents, and cost-sensitive production use.
- **GPT-5.4 nano** — Smallest and cheapest GPT-5.4 variant. Best for bulk extraction, classification, ranking, and simple support tasks.
- **o3 / o4-mini** — Still available, but generally superseded by GPT-5.4 / GPT-5.4 mini for new recommendations.

### Google
- **Gemini 2.5 Pro** — Flagship Gemini model for complex reasoning, coding, and document-heavy analysis.
- **Gemini 2.5 Flash** — Best price/performance default for lower-latency reasoning and general agent tasks.
- **Gemini 2.5 Flash-Lite** — Fastest and cheapest current Gemini 2.5 option for structured, high-volume workloads.

### Kimi (Moonshot)
- **Kimi K2.5** — Kimi's most intelligent current general model. Supports text + image input plus thinking and non-thinking modes.
- **Kimi K2 Thinking** — Best Kimi option for deep reasoning, long-horizon research, and multi-step tool use.
- **Kimi K2** — Lower-cost code and agent workhorse when K2.5 is unnecessary.

### Ollama (Local)
- **Qwen3 235B** — Strongest current general open-weight option in Ollama for reasoning, writing, and multilingual work.
- **DeepSeek R1** — Best local reasoning specialist for math, logic, and structured analysis.
- **Llama 4 Maverick** — Strong multimodal local generalist with good writing and product-quality output.
- **Devstral 2** — Best current local specialist for agentic coding and software engineering.
- **Qwen3 30B** — Best practical mid-range local default when 200B+ class models are too heavy.
- **Llama 4 Scout / Mistral Small 3.1 / Devstral Small 2** — Smaller local options for structured work, lighter assistants, and budget deployments.

## Capability Tiers

### Tier 1: Heavy Reasoning
Roles requiring: complex multi-step reasoning, architecture, security review, legal/financial analysis, deep technical synthesis.
- **Anthropic**: Opus 4.5 (thinking: high)
- **OpenAI**: GPT-5.4 (reasoning: high)
- **Google**: Gemini 2.5 Pro (thinking: enabled)
- **Kimi**: K2 Thinking
- **Ollama**: DeepSeek R1 or Qwen3 235B

### Tier 2: Strong General
Roles requiring: solid reasoning, strong writing, reliable tool use, moderate code generation, good judgment.
- **Anthropic**: Sonnet 4.6 (thinking: medium)
- **OpenAI**: GPT-5.4 mini (reasoning: medium)
- **Google**: Gemini 2.5 Pro or Flash
- **Kimi**: K2.5
- **Ollama**: Llama 4 Maverick or Qwen3 30B

### Tier 3: Creative/Writing
Roles requiring: tone, voice, narrative quality, ideation, language sensitivity. Heavy reasoning is secondary.
- **Anthropic**: Sonnet 4.6 (thinking: low)
- **OpenAI**: GPT-5.4 (reasoning: none or low)
- **Google**: Gemini 2.5 Pro
- **Kimi**: K2.5
- **Ollama**: Llama 4 Maverick or Mistral Small 3.1

### Tier 4: Structured/Routine
Roles requiring: templates, scheduling, categorization, tracking, light coordination, simple Q&A.
- **Anthropic**: Haiku 4.5
- **OpenAI**: GPT-5.4 mini (reasoning: low). Use GPT-5.4 nano for bulk extraction/classification where quality demands are lower.
- **Google**: Gemini 2.5 Flash-Lite or Flash
- **Kimi**: K2
- **Ollama**: Qwen3 30B or Llama 4 Scout

### Tier 5: Specialized Picks
Use these when the domain matters more than the generic tier:
- **Deep research / long-horizon tool use**: Opus 4.5, GPT-5.4, K2 Thinking
- **Vision / multimodal knowledge work**: GPT-5.4, Gemini 2.5 Pro, K2.5, Llama 4 Maverick
- **Local agentic coding**: Devstral 2 or Devstral Small 2
- **Localization / multilingual**: Gemini 2.5 Pro, K2.5, Qwen3 235B

## Roster Defaults

These are the default mappings the agent profiles should use unless a role has a clearly different workload shape:

- **heavy-reasoning**: `claude-opus-4-5` / `gpt-5.4` / `gemini-2.5-pro` / `kimi-k2-thinking` / `deepseek-r1`
- **strong-general**: `claude-sonnet-4-6` / `gpt-5.4-mini` / `gemini-2.5-pro` / `kimi-k2.5` / `llama-4-maverick`
- **creative-writing**: `claude-sonnet-4-6` / `gpt-5.4` / `gemini-2.5-pro` / `kimi-k2.5` / `llama-4-maverick`
- **structured-routine**: `claude-haiku-4-5` / `gpt-5.4-mini` / `gemini-2.5-flash-lite` / `kimi-k2` / `qwen3-30b`
