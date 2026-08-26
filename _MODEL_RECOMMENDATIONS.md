# Model Recommendation Framework

_Last synced from OpenRouter: 2026-08-26_

This roster routes every profile through the Hermes stack configured in `~/.hermes/config.yaml`. The vendor-specific breakdown from the old version has been replaced with the actual providers in use: OpenRouter (paid + free), local MLX, and OpenAI Codex.

## Configured Stack

| Alias | Provider | Model | Use for |
|-------|----------|-------|---------|
| `opus` | openrouter | anthropic/claude-opus-4.7 | Heavy reasoning, deep synthesis |
| `premium` | openrouter | anthropic/claude-sonnet-4.6 | Strong general default |
| `claude` | openrouter | anthropic/claude-sonnet-4.6 | Creative writing, nuanced prose |
| `cheap` | openrouter | openrouter/free | Structured/routine work |
| `local` | mlx-local | mlx-community/Qwen2.5-7B-Instruct-4bit | Private/offline iteration |
| `local-heavy` | mlx-local | mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit | Heavier private/offline reasoning |
| `codex` | openai-codex | gpt-5.6-sol | Difficult coding and implementation |

Aliases live in `~/.hermes/config.yaml` under `model_aliases`. Tier→alias routing lives in `~/.hermes/model-map.json`.

## Capability Tiers

Every profile's `model_recommendations.tier` is one of four values. The launcher at `~/.local/bin/agent-run` resolves tier → alias → provider/model at runtime.

| Tier | Primary alias | Best overall | Default fallback chain |
|------|---------------|--------------|------------------------|
| heavy-reasoning | `opus` | anthropic/claude-opus-4.7 | opus → claude → local → codex |
| strong-general | `premium` | anthropic/claude-sonnet-4.6 | premium → local → codex |
| creative-writing | `claude` | anthropic/claude-sonnet-4.6 | claude → local → codex |
| structured-routine | `cheap` | openrouter/free | cheap → local → premium |

Legacy tier names (`analytical`, `analytical-complex`, `deep-reasoning`, `strategic-reasoning`, `structured-reasoning`) normalize to `heavy-reasoning`; `editing` normalizes to `creative-writing`.

## OpenRouter Free-Model Catalog

Full live list of free models on OpenRouter as of 2026-08-26. Grouped by provider. Context length in tokens. These are the models selected from when a roster entry falls back to `openrouter/free` or when a specific free slug is listed in a profile's `free_openrouter` array.

**Total free text LLMs: 19**

### Nvidia

| Slug | Context | Description |
|------|---------|-------------|
| `nvidia/nemotron-3.5-lightning:free` | 1,000,000 | NVIDIA Nemotron 3.5 Lightning is an open mixture-of-experts model from NVIDIA, with 3B active parameters out of 30B total. It is suited… |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1,000,000 | NVIDIA Nemotron 3 Ultra is an open frontier-reasoning and orchestration model from NVIDIA, with 55B active parameters out of 550B total… |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262,144 | NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and… |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256,000 | NVIDIA Nemotron™ 3 Nano Omni is a 30B-A3B open multimodal model designed to function as a perception and context sub-agent in enterprise… |
| `nvidia/nemotron-3.5-content-safety:free` | 128,000 | NVIDIA Nemotron 3.5 Content Safety is a compact 4B-parameter multimodal guardrail model from NVIDIA, fine-tuned from Google Gemma-3-4B.… |

### Google

| Slug | Context | Description |
|------|---------|-------------|
| `google/gemma-4-26b-a4b-it:free` | 262,144 | Gemma 4 26B A4B IT is an instruction-tuned Mixture-of-Experts (MoE) model from Google DeepMind. Despite 25.2B total parameters, only… |
| `google/gemma-4-31b-it:free` | 262,144 | Gemma 4 31B Instruct is Google DeepMind's 30.7B dense multimodal model supporting text and image input with text output. Features a 256K… |

### Minimax

| Slug | Context | Description |
|------|---------|-------------|
| `minimax/minimax-m3:free` | 1,048,576 | MiniMax-M3 is a multimodal foundation model from MiniMax. It supports text, image, and video inputs with text output, a 1M-token context… |
| `minimax/minimax-m2.7:free` | 196,608 | MiniMax-M2.7 is a next-generation large language model designed for autonomous, real-world productivity and continuous improvement.… |

### Poolside

| Slug | Context | Description |
|------|---------|-------------|
| `poolside/laguna-s-2.1:free` | 262,144 | Laguna S 2.1 is the latest coding agent model from [Poolside](<https://poolside.ai/>). Laguna S 2.1 is a 118B total parameter model with… |
| `poolside/laguna-xs-2.1:free` | 262,144 | Laguna XS 2.1 is the latest coding agent model in the 33B-A3B category from [Poolside](https://poolside.ai/) and a step forward from… |

### Thinkingmachines

| Slug | Context | Description |
|------|---------|-------------|
| `thinkingmachines/inkling-small:free` | 1,048,576 | Inkling Small is an open-weight multimodal mixture-of-experts model from Thinking Machines Lab, with 12B active parameters out of 276B… |
| `thinkingmachines/inkling:free` | 1,048,576 | Inkling is an open-weight multimodal mixture-of-experts model from Thinking Machines Lab, with 41B active parameters out of 975B total.… |

### Cohere

| Slug | Context | Description |
|------|---------|-------------|
| `cohere/north-mini-code:free` | 256,000 | North Mini Code is Cohere's first agentic coding model and the debut of its North family. A sparse mixture-of-experts model with 30B… |

### Dots Studio

| Slug | Context | Description |
|------|---------|-------------|
| `dots-studio/dots-3-note-preview:free` | 512,000 | Dots3-Note Preview is an open-weight mixture-of-experts model from Dots Studio, with 16B active parameters out of 280B total. It is the… |

### Liquid

| Slug | Context | Description |
|------|---------|-------------|
| `liquid/lfm-2.5-2.6b:free` | 65,536 | LFM2.5-2.6B is a compact reasoning model from Liquid AI. It is suited for agent workflows, data extraction, RAG, and long-context… |

### Openrouter

| Slug | Context | Description |
|------|---------|-------------|
| `openrouter/free` | 200,000 | The simplest way to get free inference. openrouter/free is a router that selects free models at random from the models available on… |

### Stealth

| Slug | Context | Description |
|------|---------|-------------|
| `stealth/ox-alpha` | 1,048,576 | Ox Alpha is a reasoning model designed for coding, sustained agentic work, and production workloads. It is suited for long-horizon… |

### Z Ai

| Slug | Context | Description |
|------|---------|-------------|
| `z-ai/glm-5.2:free` | 256,000 | GLM 5.2 is a large-scale reasoning model from Z.ai. It supports text input and output with a 1M-token context window, and is suited for… |

## How Roster Entries Use This

Each `roster_entry.json` (and the mirrored entry in `roster.json`) carries a `model_recommendations` block shaped like:

```json
{
  "tier": "strong-general",
  "best_overall": "anthropic/claude-sonnet-4.6",
  "primary":   { "provider": "openrouter",   "model": "anthropic/claude-sonnet-4.6" },
  "secondary": { "provider": "openrouter",   "model": "anthropic/claude-opus-4.7"   },
  "cheap":     { "provider": "openrouter",   "model": "openrouter/free"             },
  "local":     { "provider": "mlx-local", "model": "mlx-community/Qwen2.5-7B-Instruct-4bit" },
  "codex":     { "provider": "openai-codex", "model": "gpt-5.6-sol" },
  "free_openrouter": [ "nousresearch/hermes-3-llama-3.1-405b:free", "..." ],
  "notes": "..."
}
```

Downstream tooling (`agent-run`) reads `hermes_model_hint.alias` to pick which entry to route to. `free_openrouter` is an enumerated alternate pool for when explicit model selection beats the meta-router.

## Refresh Procedure

To resync this file after OpenRouter's free tier changes:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/hermes-roster-model-sync/scripts/sync.py
```
