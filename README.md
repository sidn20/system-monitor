# 🖥️ System Monitor

A live terminal dashboard that monitors system performance in real time,
built with Python and the `rich` library on Ubuntu Linux.

Integrates with [ml-benchmark](https://github.com/sidn20/ml-benchmark)
to display live benchmark results alongside system metrics.

![System Monitor Dashboard](screenshot.png)

## Features

- **Live CPU bars** per core with green/yellow/red color coding
- **CPU history sparkline** showing last 20 readings as unicode blocks
- **RAM usage** with visual progress bar and free memory
- **Disk usage** with CRITICAL/WARNING/OK threshold alerts
- **Real-time network speed** in KB/s or MB/s (not just total bytes)
- **Top 5 processes** by CPU usage with PID and RAM %
- **Live benchmark panel** pulling results from ml-benchmark automatically
- Refreshes every 0.5 seconds

## Demo
System Monitor — 2026-06-11 10:42:16
┌─────────────────────────────────────────────────────────────┐
│ CPU Metrics        Value                                     │
│ Overall CPU        [█░░░░░░░░░░░░░░░░░░░]   5.9%           │
│ CPU History        ▄ ▄ █ ▄ ▁ ▄ ░           5.9%            │
│ Frequency          2304 MHz                                  │
│                                                              │
│ Memory & Disk      Value                                     │
│ RAM Usage          [███░░░░░░░░░░░░░░░░░]  2.2/9.7 GB      │
│ Disk Status        ⚠ CRITICAL: 92.5% full                   │
│ Net Upload         0.2 KB/s  (total: 0.2 MB)                │
│ Net Download       0.2 KB/s  (total: 4.0 MB)                │
│                                                              │
│ Benchmark History  Value                                     │
│ Last Run           2026-06-11 11:30:01                      │
│ Mean Latency       141.5 ms                                  │
└─────────────────────────────────────────────────────────────┘

## Quick Start

```bash
# Install dependencies
pip3 install psutil rich

# Run
python3 monitor.py

# Exit with Ctrl+C
```

## Color Coding

| Color | Meaning |
|-------|---------|
| 🟢 Green | Normal — under 60% |
| 🟡 Yellow | Warning — 60% to 85% |
| 🔴 Red | Critical — above 85% |

## Disk Alerts

| Status | Threshold |
|--------|-----------|
| ✓ OK | Under 75% full |
| ⚠ WARNING | 75% to 90% full |
| ⚠ CRITICAL | Above 90% full |

## Benchmark Integration

If you have the [ml-benchmark](https://github.com/sidn20/ml-benchmark)
project set up, the dashboard automatically reads
`~/ml_benchmark/benchmark_log.csv` and shows live results —
no configuration needed.

Displays last run timestamp, mean/min/max latency, stdev,
and a 3-run history with color coded latency values.

## Tech Stack

| Tool | Purpose |
|------|---------|
| `psutil` | Reading CPU, RAM, disk, network from Linux kernel |
| `rich` | Terminal UI — tables, colors, live rendering |
| `csv` | Reading benchmark log from ml-benchmark project |
| `datetime` | Timestamping each refresh |

## What I Learned

- Building live terminal UIs with `rich.live.Live`
- Real-time network speed via delta measurements between two readings
- CPU sparkline history using unicode block characters `▁▂▃▄▅▆▇█`
- Color-coded threshold alerting system
- Integrating two separate projects to share live data
- Headless Python on Ubuntu Linux without a display server

## Related

[ml-benchmark](https://github.com/sidn20/ml-benchmark) —
ML inference benchmarking tool this dashboard integrates with
