# Model Recommendation Framework

_Last synced from OpenRouter: 2026-04-28_

This roster routes every profile through the Hermes stack configured in `~/.hermes/config.yaml`. The vendor-specific breakdown from the old version has been replaced with the actual providers in use: OpenRouter (paid + free), local MLX, and OpenAI Codex.

## Configured Stack

| Alias      | Provider      | Model                                                    | Use for                                |
|------------|---------------|----------------------------------------------------------|----------------------------------------|
| `opus`     | openrouter    | anthropic/claude-opus-4.7                                | Heavy reasoning, deep synthesis        |
| `premium`  | openrouter    | anthropic/claude-sonnet-4.6                              | Strong general default                 |
| `claude`   | openrouter    | anthropic/claude-sonnet-4.6                              | Creative writing, nuanced prose        |
| `cheap`    | openrouter    | openrouter/free (meta-router over the free pool)         | Structured/routine work                |
| `local`    | mlx-local     | mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit           | Private/offline iteration              |
| `codex`    | openai-codex  | gpt-5.5                                                  | Last-resort difficult coding           |

Aliases live in `~/.hermes/config.yaml` under `model_aliases`. Tier→alias routing lives in `~/.hermes/model-map.json`.

## Capability Tiers

Every profile's `model_recommendations.tier` is one of four values. The launcher at `~/.hermes/hermes-agent/scripts/agent-run.sh` resolves tier → alias → provider/model at runtime.

| Tier                | Primary alias | Best overall                        | Default fallback chain                |
|---------------------|---------------|-------------------------------------|---------------------------------------|
| heavy-reasoning     | `opus`        | anthropic/claude-opus-4.7           | opus → claude → local → codex         |
| strong-general      | `premium`     | anthropic/claude-sonnet-4.6         | premium → local → codex               |
| creative-writing    | `claude`      | anthropic/claude-sonnet-4.6         | claude → local → codex                |
| structured-routine  | `cheap`       | openrouter/free                     | cheap → local → premium               |

Legacy tier names (`analytical`, `analytical-complex`, `deep-reasoning`, `strategic-reasoning`, `structured-reasoning`) normalize to `heavy-reasoning`; `editing` normalizes to `creative-writing`.

## OpenRouter Free-Model Catalog

Full live list of free models on OpenRouter as of 2026-04-28. Grouped by provider. Context length in tokens. These are the models selected from when a roster entry falls back to `openrouter/free` or when a specific free slug is listed in a profile's `free_openrouter` array.

**Total free text LLMs: 30**

### Google

| Slug | Context | Description |
|------|---------|-------------|
| `google/gemma-4-26b-a4b-it:free` | 262,144 | Gemma 4 26B A4B IT is an instruction-tuned Mixture-of-Experts (MoE) model from Google DeepMind. Despite 25.2B total parameters, only… |
| `google/gemma-4-31b-it:free` | 262,144 | Gemma 4 31B Instruct is Google DeepMind's 30.7B dense multimodal model supporting text and image input with text output. Features a 256K… |
| `google/gemma-3-27b-it:free` | 131,072 | Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens,… |
| `google/gemma-3-4b-it:free` | 32,768 | Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens,… |
| `google/gemma-3-12b-it:free` | 32,768 | Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens,… |
| `google/gemma-3n-e2b-it:free` | 8,192 | Gemma 3n E2B IT is a multimodal, instruction-tuned model developed by Google DeepMind, designed to operate efficiently at an effective… |
| `google/gemma-3n-e4b-it:free` | 8,192 | Gemma 3n E4B-it is optimized for efficient execution on mobile and low-resource devices, such as phones, laptops, and tablets. It… |

### Nvidia

| Slug | Context | Description |
|------|---------|-------------|
| `nvidia/nemotron-3-super-120b-a12b:free` | 262,144 | NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and… |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256,000 | NVIDIA Nemotron™ 3 Nano Omni is a 30B-A3B open multimodal model designed to function as a perception and context sub-agent in enterprise… |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256,000 | NVIDIA Nemotron 3 Nano 30B A3B is a small language MoE model with highest compute efficiency and accuracy for developers to build… |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 128,000 | NVIDIA Nemotron Nano 2 VL is a 12-billion-parameter open multimodal reasoning model designed for video understanding and document… |
| `nvidia/nemotron-nano-9b-v2:free` | 128,000 | NVIDIA-Nemotron-Nano-9B-v2 is a large language model (LLM) trained from scratch by NVIDIA, and designed as a unified model for both… |

### Inclusionai

| Slug | Context | Description |
|------|---------|-------------|
| `inclusionai/ling-2.6-1t:free` | 262,144 | Ling-2.6-1T is an instant (instruct) model from inclusionAI and the company’s trillion-parameter flagship, designed for real-world… |
| `inclusionai/ling-2.6-flash:free` | 262,144 | Ling-2.6-flash is an instant (instruct) model from inclusionAI with 104B total parameters and 7.4B active parameters, designed for… |

### Liquid

| Slug | Context | Description |
|------|---------|-------------|
| `liquid/lfm-2.5-1.2b-thinking:free` | 32,768 | LFM2.5-1.2B-Thinking is a lightweight reasoning-focused model optimized for agentic tasks, data extraction, and RAG—while still running… |
| `liquid/lfm-2.5-1.2b-instruct:free` | 32,768 | LFM2.5-1.2B-Instruct is a compact, high-performance instruction-tuned model built for fast on-device AI. It delivers strong chat quality… |

### Meta Llama

| Slug | Context | Description |
|------|---------|-------------|
| `meta-llama/llama-3.2-3b-instruct:free` | 131,072 | Llama 3.2 3B is a 3-billion-parameter multilingual large language model, optimized for advanced natural language processing tasks like… |
| `meta-llama/llama-3.3-70b-instruct:free` | 65,536 | The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and instruction tuned generative model in 70B (text in/text… |

### Openai

| Slug | Context | Description |
|------|---------|-------------|
| `openai/gpt-oss-120b:free` | 131,072 | gpt-oss-120b is an open-weight, 117B-parameter Mixture-of-Experts (MoE) language model from OpenAI designed for high-reasoning, agentic,… |
| `openai/gpt-oss-20b:free` | 131,072 | gpt-oss-20b is an open-weight 21B parameter model released by OpenAI under the Apache 2.0 license. It uses a Mixture-of-Experts (MoE)… |

### Poolside

| Slug | Context | Description |
|------|---------|-------------|
| `poolside/laguna-xs.2:free` | 131,072 | Laguna XS.2 is the second-generation model in the XS size class from [Poolside](https://poolside.ai), their efficient coding agent… |
| `poolside/laguna-m.1:free` | 131,072 | Laguna M.1 is the flagship coding agent model from [Poolside](https://poolside.ai), optimized for complex software engineering tasks.… |

### Qwen

| Slug | Context | Description |
|------|---------|-------------|
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262,144 | Qwen3-Next-80B-A3B-Instruct is an instruction-tuned chat model in the Qwen3-Next series optimized for fast, stable responses without… |
| `qwen/qwen3-coder:free` | 262,000 | Qwen3-Coder-480B-A35B-Instruct is a Mixture-of-Experts (MoE) code generation model developed by the Qwen team. It is optimized for… |

### Cognitivecomputations

| Slug | Context | Description |
|------|---------|-------------|
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | 32,768 | Venice Uncensored Dolphin Mistral 24B Venice Edition is a fine-tuned variant of Mistral-Small-24B-Instruct-2501, developed by dphn.ai in… |

### Minimax

| Slug | Context | Description |
|------|---------|-------------|
| `minimax/minimax-m2.5:free` | 196,608 | MiniMax-M2.5 is a SOTA large language model designed for real-world productivity. Trained in a diverse range of complex real-world… |

### Nousresearch

| Slug | Context | Description |
|------|---------|-------------|
| `nousresearch/hermes-3-llama-3.1-405b:free` | 131,072 | Hermes 3 is a generalist language model with many improvements over Hermes 2, including advanced agentic capabilities, much better… |

### Openrouter

| Slug | Context | Description |
|------|---------|-------------|
| `openrouter/free` | 200,000 | The simplest way to get free inference. openrouter/free is a router that selects free models at random from the models available on… |

### Tencent

| Slug | Context | Description |
|------|---------|-------------|
| `tencent/hy3-preview:free` | 262,144 | Hy3 preview is a high-efficiency Mixture-of-Experts model from Tencent designed for agentic workflows and production use. It supports… |

### Z Ai

| Slug | Context | Description |
|------|---------|-------------|
| `z-ai/glm-4.5-air:free` | 131,072 | GLM-4.5-Air is the lightweight variant of our latest flagship model family, also purpose-built for agent-centric applications. Like… |

## How Roster Entries Use This

Each `roster_entry.json` (and the mirrored entry in `roster.json`) carries a `model_recommendations` block shaped like:

```json
{
  "tier": "strong-general",
  "best_overall": "anthropic/claude-sonnet-4.6",
  "primary":   { "provider": "openrouter",   "model": "anthropic/claude-sonnet-4.6" },
  "secondary": { "provider": "openrouter",   "model": "anthropic/claude-opus-4.7"   },
  "cheap":     { "provider": "openrouter",   "model": "openrouter/free"             },
  "local":     { "provider": "mlx-local",    "model": "mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit" },
  "codex":     { "provider": "openai-codex", "model": "gpt-5.5" },
  "free_openrouter": [ "nousresearch/hermes-3-llama-3.1-405b:free", "..." ],
  "notes": "..."
}
```

Downstream tooling (agent-run.sh) reads `hermes_model_hint.alias` to pick which entry to route to. `free_openrouter` is an enumerated alternate pool for when explicit model selection beats the meta-router.

## Refresh Procedure

To resync this file after OpenRouter's free tier changes:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/hermes-roster-model-sync/scripts/sync.py
```
