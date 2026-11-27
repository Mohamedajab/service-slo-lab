from pathlib import Path
import pytest
from slo_report import load, percentile, report


def test_nearest_rank_percentile():
    assert percentile([50, 10, 40, 20, 30], .95) == 50


def test_report_shows_exhausted_error_budget():
    samples = [{"status": 200, "latency_ms": 100}] * 99 + [{"status": 503, "latency_ms": 900}]
    result = report(samples, .99, 500)
    assert result["availability"] == .99
    assert result["availability_met"] is True
    assert result["latency_met"] is True
    assert result["error_budget_remaining"] == 0


def test_bad_log_names_line(tmp_path: Path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"status": 200}\n')
    with pytest.raises(ValueError, match="line 1"):
        load(path)


@pytest.mark.parametrize(
    "requests,target,allowed", [(5, .8, 1), (10, .9, 1), (100, .99, 1), (3, .9, 0)]
)
def test_error_budget_rounds_down_without_float_error(requests, target, allowed):
    samples = [{"status": 200, "latency_ms": 100}] * (requests - 1)
    samples.append({"status": 503, "latency_ms": 100})

    result = report(samples, target)

    assert result["allowed_failures"] == allowed
    assert result["error_budget_remaining"] == allowed - 1
    assert result["availability_met"] is (allowed >= 1)
