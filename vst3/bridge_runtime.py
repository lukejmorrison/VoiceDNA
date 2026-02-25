from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


def _blend_embeddings(parent_a: VoiceDNA, parent_b: VoiceDNA, inherit_a: float, inherit_b: float, randomness: float) -> list[float]:
    total = max(0.0001, inherit_a + inherit_b)
    weight_a = inherit_a / total
    weight_b = inherit_b / total

    output: list[float] = []
    jitter_scale = max(0.0, min(100.0, randomness)) / 100.0 * 0.08

    for a_value, b_value in zip(parent_a.core_embedding, parent_b.core_embedding):
        blended = (a_value * weight_a) + (b_value * weight_b)
        jitter = random.uniform(-1.0, 1.0) * jitter_scale
        output.append(max(-1.0, min(1.0, blended + jitter)))

    return output


def run_process(args: argparse.Namespace) -> int:
    dna = VoiceDNA.load_encrypted(password=args.password, filepath=args.dna_path)
    dna.imprint_strength = max(0.0, min(1.0, args.imprint_strength))

    processor = VoiceDNAProcessor()
    input_bytes = Path(args.input_wav).read_bytes()

    params = {
        "audio_format": "wav",
        "base_model": args.base_model,
        "imprint_converter.mode": "simple",
        "force_age": float(args.force_age),
    }

    output_bytes = processor.process(input_bytes, dna, params)
    Path(args.output_wav).write_bytes(output_bytes)

    report = processor.get_last_report()
    print(json.dumps({"status": "ok", "mode": "process", "report": report}, ensure_ascii=False))
    return 0


def run_birth(args: argparse.Namespace) -> int:
    parent_a = VoiceDNA.create_new(str(args.parent_a), user_name="parent_a")
    parent_b = VoiceDNA.create_new(str(args.parent_b), user_name="parent_b")

    child = VoiceDNA.create_new(
        imprint_audio_description=f"Child of {Path(args.parent_a).name} + {Path(args.parent_b).name}",
        user_name=args.child_user,
    )

    child.core_embedding = _blend_embeddings(
        parent_a,
        parent_b,
        inherit_a=args.inherit_a,
        inherit_b=args.inherit_b,
        randomness=args.randomness,
    )

    child.unique_traits = list(dict.fromkeys(parent_a.unique_traits + parent_b.unique_traits + child.unique_traits))
    child.imprint_strength = max(0.0, min(1.0, (args.inherit_a + args.inherit_b) / 200.0))
    child.morph_allowance = max(0.02, min(0.35, 0.05 + (args.randomness / 100.0) * 0.20))

    output = Path(args.out)
    if output.suffixes[-2:] != [".voicedna", ".enc"]:
        output = output.with_suffix(output.suffix + ".voicedna.enc")
    output.parent.mkdir(parents=True, exist_ok=True)

    child.save_encrypted(password=args.password, filepath=str(output))

    payload = {
        "status": "ok",
        "mode": "birth",
        "child_id": child.get_recognition_id(),
        "out": str(output),
        "inherit_a": args.inherit_a,
        "inherit_b": args.inherit_b,
        "randomness": args.randomness,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VoiceDNA VST3 runtime bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process_parser = subparsers.add_parser("process", help="Run real-time filter processing")
    process_parser.add_argument("--dna-path", required=True)
    process_parser.add_argument("--password", required=True)
    process_parser.add_argument("--input-wav", required=True)
    process_parser.add_argument("--output-wav", required=True)
    process_parser.add_argument("--base-model", default="vst3_reaper")
    process_parser.add_argument("--force-age", type=float, default=12.0)
    process_parser.add_argument("--imprint-strength", type=float, default=0.68)
    process_parser.set_defaults(func=run_process)

    birth_parser = subparsers.add_parser("birth", help="Create child VoiceDNA from two parent audio files")
    birth_parser.add_argument("--parent-a", required=True)
    birth_parser.add_argument("--parent-b", required=True)
    birth_parser.add_argument("--child-user", required=True)
    birth_parser.add_argument("--inherit-a", type=float, default=50.0)
    birth_parser.add_argument("--inherit-b", type=float, default=50.0)
    birth_parser.add_argument("--randomness", type=float, default=10.0)
    birth_parser.add_argument("--out", required=True)
    birth_parser.add_argument("--password", required=True)
    birth_parser.set_defaults(func=run_birth)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
