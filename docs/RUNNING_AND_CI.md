# Running the lab and interpreting its exit code

Use Python 3.11 or newer and run commands from the repository root. The report
script needs only the standard library. Install `pytest` to run the test suite;
no monitoring server, cloud credentials or live traffic is required.

## Development setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest
```

macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest
```

Use the environment's Python path instead of `python` below if it is not activated.

## The supplied failing window

```bash
python slo_report.py examples/service.jsonl --availability 0.99 --latency-ms 500
```

This is an intentional failure, not a broken installation. The four samples
contain three available requests and one 503 response. The printed report is:

```json
{
  "requests": 4,
  "availability": 0.75,
  "availability_target": 0.99,
  "failed_requests": 1,
  "allowed_failures": 0,
  "error_budget_remaining": -1,
  "p95_latency_ms": 890.0,
  "latency_target_ms": 500.0,
  "availability_met": false,
  "latency_met": false
}
```

Its exit status is 1. The p95 is the maximum sample in this small window, and
the availability budget permits zero failures after rounding down.

For a passing demonstration using the **same** data, choose deliberately looser
targets:

```bash
python slo_report.py examples/service.jsonl --availability 0.75 --latency-ms 900
```

This returns status 0: one failure is permitted and the 890 ms p95 is below
900 ms. These values are illustrative, not recommended production objectives.

## Shell and CI behaviour

Inspect the exit status immediately after running the report:

```powershell
$LASTEXITCODE
```

```bash
echo $?
```

The CLI returns 0 only when both targets pass, and 1 when either is missed.
Invalid input can also fail with a Python exception. A nonzero result alone
does not distinguish an SLO miss from an input or configuration problem.
Review the JSON report and error output as well.

The repository's GitHub workflow runs unit tests, not the intentionally failing
example as a deployment gate. If you use the CLI as a gate elsewhere, supply
your own validated telemetry and explicit targets, and preserve the JSON output
as an artefact before handling the exit status.

## Troubleshooting and boundaries

- Empty files and malformed rows are rejected; blank lines are not skipped.
- Availability targets must be greater than 0 and at most 1; latency targets
  must be positive.
- Extra fields such as the example's timestamps do not select a time window.
  Every input row contributes to the report; filter your measurement window first.
- A negative remaining error budget means the allowed failure count was exceeded.
- A 4xx response counts as available in this educational model. Check whether
  that matches your real service before using its result operationally.

See [Design notes](DESIGN.md) for formulas, rounding, limitations and proposed
production extensions. The lab does not calculate burn rates or rolling windows.
