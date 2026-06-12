---

## Usage

```bash
# Run the dashboard
python3 monitor.py

# Press Ctrl+C to exit
```

---

## Color Coding

| Color  | Meaning                        |
|--------|--------------------------------|
| Green  | Normal — under 60%             |
| Yellow | Warning — 60% to 85%          |
| Red    | Critical — above 85%           |

---

## Disk Alerts

| Status   | Threshold       |
|----------|-----------------|
| OK       | Under 75% full  |
| WARNING  | 75% to 90% full |
| CRITICAL | Above 90% full  |

---

## Benchmark Integration

If you have the [ml-benchmark](https://github.com/sidn20/ml-benchmark)
project running, the dashboard automatically reads
`~/ml_benchmark/benchmark_log.csv` and displays:

- Timestamp of last benchmark run
- Mean, min, max latency
- Stdev (stability indicator)
- Last 3 run history with color coded latency

No configuration needed — it reads the file automatically.

---

## Requirements

```bash
pip3 install psutil rich
```

---

## What I learned

- `rich` library — building professional terminal UIs in Python
- Live updating dashboards with `rich.live.Live`
- Real-time network speed calculation using delta measurements
- CPU sparkline history using unicode block characters
- Color-coded threshold alerting
- Integrating two separate projects to share live data
