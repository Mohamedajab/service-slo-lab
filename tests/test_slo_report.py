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
