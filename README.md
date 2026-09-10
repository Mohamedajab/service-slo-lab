# Service SLO Lab

A small reliability script that turns JSONL request samples into an availability,
p95 latency and error-budget report.

```powershell
python slo_report.py examples/service.jsonl --availability 0.99 --latency-ms 500
python -m pytest
```

The example intentionally fails its targets and exits with status 1. HTTP
statuses below 500 count as available; that is a deliberate simplification.
A real service may treat timeouts, incorrect responses and selected 4xx codes
differently.

The p95 uses the nearest-rank definition. Small windows make percentiles jumpy,
and `floor` makes the allowed failure count strict for small samples. Production
monitoring should use a meaningful rolling window and enough traffic.

Main idea to explain: an error budget converts a reliability target into the
number of failed requests the service can tolerate during the measurement window.
