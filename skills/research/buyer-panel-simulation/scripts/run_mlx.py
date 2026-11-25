"""Answer one packet at a time with an installed local MLX chat model."""
import argparse
import json
from pathlib import Path
import sys

from panel import fields, read, validate_answer


def decode(text):
    result = text.strip()
    if result.startswith("```json\n") and result.endswith("\n```"):
        result = result[8:-4]
    answer = json.loads(result)
    validate_answer(answer)
    return {key: answer[key] for key in ("offer_excerpt", "action", "reason")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packets")
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--model-label", help="model name and revision for the run record")
    args = parser.parse_args()
    if not args.model_dir.is_dir():
        parser.error("--model-dir must be an installed local model directory")
    packets = read(args.packets)
    if not isinstance(packets, list) or not packets:
        raise ValueError("expected a nonempty packet list")
    for packet in packets:
        fields(packet, ["trial", "prompt"], "packet")
    from mlx_lm import generate, load, __version__
    from mlx_lm.sample_utils import make_sampler
    model, tokenizer = load(str(args.model_dir.resolve()))
    answers = []
    for packet in packets:
        prompt = tokenizer.apply_chat_template([{"role": "user", "content": packet["prompt"]}],
                                               tokenize=False, add_generation_prompt=True,
                                               enable_thinking=False)
        text = generate(model, tokenizer, prompt=prompt, sampler=make_sampler(temp=0),
                        max_tokens=160, verbose=False)
        try:
            answer = decode(text)
        except ValueError as exc:
            raise ValueError(f"invalid model answer for trial {packet['trial']}: {exc}") from exc
        answers.append({"trial": packet["trial"], **answer})
    label = args.model_label or args.model_dir.name
    print(json.dumps({"generator": f"{label}; mlx-lm {__version__}; greedy; max_tokens=160",
                      "context_mode": "independent", "responses": answers}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ImportError, ValueError, OSError) as error:
        sys.exit(str(error))
