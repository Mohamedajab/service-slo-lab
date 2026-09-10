"""Calculate a basic availability and latency SLO report from JSONL."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def percentile(values: list[float], percentage: float) -> float:
    if not values:
        raise ValueError("at least one latency is required")
    ordered = sorted(values)
    index = max(0, math.ceil(percentage * len(ordered)) - 1)
    return ordered[index]


def load(path: Path) -> list[dict]:
    samples = []
    for number, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        try:
            sample = json.loads(line)
            status, latency = int(sample["status"]), float(sample["latency_ms"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise ValueError(f"invalid sample on line {number}") from error
        if latency < 0:
            raise ValueError(f"negative latency on line {number}")
        samples.append({"status": status, "latency_ms": latency})
    if not samples:
        raise ValueError("log contains no samples")
    return samples


def report(samples: list[dict], availability_target=0.99, latency_target_ms=500) -> dict:
    if not 0 < availability_target <= 1 or latency_target_ms <= 0:
        raise ValueError("targets must be positive; availability cannot exceed 1")
    good = sum(200 <= row["status"] < 500 for row in samples)
    failures = len(samples) - good
    allowed = math.floor(len(samples) * (1 - availability_target))
    p95 = percentile([row["latency_ms"] for row in samples], .95)
    return {"requests": len(samples), "availability": good / len(samples),
            "availability_target": availability_target, "failed_requests": failures,
            "allowed_failures": allowed, "error_budget_remaining": allowed - failures,
            "p95_latency_ms": p95, "latency_target_ms": latency_target_ms,
            "availability_met": failures <= allowed, "latency_met": p95 <= latency_target_ms}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--availability", type=float, default=.99)
    parser.add_argument("--latency-ms", type=float, default=500)
    args = parser.parse_args()
    result = report(load(args.log), args.availability, args.latency_ms)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["availability_met"] and result["latency_met"] else 1)
