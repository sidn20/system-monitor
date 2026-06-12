import psutil
import time
import csv
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.console import Group
from rich import box
from datetime import datetime

def get_cpu_bar(percent: float, width: int = 20) -> Text:
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    color = "green" if percent < 60 else "yellow" if percent < 85 else "red"
    return Text(f"[{bar}] {percent:5.1f}%", style=color)

def get_ram_bar(percent: float, used_gb: float, total_gb: float, width: int = 20) -> Text:
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    color = "green" if percent < 60 else "yellow" if percent < 85 else "red"
    return Text(f"[{bar}] {used_gb:.1f}/{total_gb:.1f} GB", style=color)

def get_disk_warning(percent: float) -> Text:
    if percent >= 90:
        return Text(f"⚠ CRITICAL: {percent:.1f}% full — free up space!", style="bold red")
    elif percent >= 75:
        return Text(f"⚠ WARNING: {percent:.1f}% full", style="bold yellow")
    else:
        return Text(f"✓ OK: {percent:.1f}% used", style="green")

def get_sparkline(history: list, width: int = 20) -> Text:
    if len(history) < 2:
        return Text("collecting...", style="dim")
    blocks = " ▁▂▃▄▅▆▇█"
    max_val = max(history) or 1
    sparkline = ""
    for val in history[-width:]:
        idx = int((val / max_val) * (len(blocks) - 1))
        sparkline += blocks[idx]
    color = "green" if history[-1] < 60 else "yellow" if history[-1] < 85 else "red"
    return Text(f"{sparkline} {history[-1]:.1f}%", style=color)

def format_speed(kb_per_sec: float) -> str:
    if kb_per_sec > 1024:
        return f"{kb_per_sec/1024:.2f} MB/s"
    return f"{kb_per_sec:.1f} KB/s"

def get_latest_benchmark(log_path: str = "/home/ubuntu/ml_benchmark/benchmark_log.csv") -> Table:
    bench_table = Table(box=box.SIMPLE, show_header=True, header_style="bold green")
    bench_table.add_column("Benchmark History", style="green", width=22)
    bench_table.add_column("Value", width=38)

    try:
        with open(log_path, "r") as f:
            rows = list(csv.DictReader(f))

        if not rows:
            bench_table.add_row("Status", "No data yet")
            return bench_table

        valid = [r for r in rows if r.get("mean_ms") and r["mean_ms"].strip()][-3:]
        latest = valid[-1]

        mean = float(latest["mean_ms"])
        color = "green" if mean < 200 else "yellow" if mean < 300 else "red"

        bench_table.add_row("Last Run", latest["timestamp"])
        bench_table.add_row("Mean Latency", Text(f"{mean:.1f} ms", style=color))
        bench_table.add_row("Min Latency", f"{float(latest['min_ms']):.1f} ms")
        bench_table.add_row("Max Latency", f"{float(latest['max_ms']):.1f} ms")
        bench_table.add_row("Stdev", f"{float(latest['stdev_ms']):.1f} ms")
        bench_table.add_row("─" * 20, "─" * 30)
        bench_table.add_row("Run History", "Mean (ms)")

        for row in valid:
            if row.get("mean_ms") and row["mean_ms"].strip():
                m = float(row["mean_ms"])
                c = "green" if m < 200 else "yellow" if m < 300 else "red"
                bench_table.add_row(
                    row["timestamp"][11:16],
                    Text(f"{m:.1f} ms", style=c)
                )

    except FileNotFoundError:
        bench_table.add_row("Status", "benchmark_log.csv not found")
    except Exception as e:
        bench_table.add_row("Error", str(e)[:30])

    return bench_table

if __name__ == "__main__":
    print("Starting system monitor... Press Ctrl+C to exit\n")
    time.sleep(1)

    cpu_history = []

    with Live(refresh_per_second=2, screen=True) as live:
        while True:
            # CPU
            cpu_total = psutil.cpu_percent(interval=0.1)
            cpu_cores = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            cpu_history.append(cpu_total)
            if len(cpu_history) > 20:
                cpu_history.pop(0)

            # RAM
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / 1024**3
            ram_total_gb = ram.total / 1024**3

            # Disk
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / 1024**3
            disk_total_gb = disk.total / 1024**3

            # Network speed
            net1 = psutil.net_io_counters()
            time.sleep(0.5)
            net2 = psutil.net_io_counters()
            net_sent_speed = (net2.bytes_sent - net1.bytes_sent) / 1024 / 0.5
            net_recv_speed = (net2.bytes_recv - net1.bytes_recv) / 1024 / 0.5
            net_sent_total_mb = net2.bytes_sent / 1024**2
            net_recv_total_mb = net2.bytes_recv / 1024**2

            # Top processes
            processes = sorted(
                psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                key=lambda p: p.info['cpu_percent'] or 0,
                reverse=True
            )[:5]

            # CPU table
            cpu_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
            cpu_table.add_column("CPU Metrics", style="cyan", width=25)
            cpu_table.add_column("Value", width=35)
            cpu_table.add_row("Overall CPU", get_cpu_bar(cpu_total))
            cpu_table.add_row("CPU History", get_sparkline(cpu_history))
            cpu_table.add_row("Frequency", f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A")
            cpu_table.add_row("Core Count", str(cpu_count))
            for i, pct in enumerate(cpu_cores[:4]):
                cpu_table.add_row(f"Core {i}", get_cpu_bar(pct))

            # Memory table
            mem_table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
            mem_table.add_column("Memory & Disk", style="magenta", width=25)
            mem_table.add_column("Value", width=35)
            mem_table.add_row("RAM Usage", get_ram_bar(ram.percent, ram_used_gb, ram_total_gb))
            mem_table.add_row("RAM Free", f"{(ram.available / 1024**3):.1f} GB")
            mem_table.add_row("Disk Usage", get_ram_bar(disk.percent, disk_used_gb, disk_total_gb))
            mem_table.add_row("Disk Status", get_disk_warning(disk.percent))
            mem_table.add_row("Disk Free", f"{(disk.free / 1024**3):.1f} GB")
            mem_table.add_row("Net Upload", f"{format_speed(net_sent_speed)} (total: {net_sent_total_mb:.1f} MB)")
            mem_table.add_row("Net Download", f"{format_speed(net_recv_speed)} (total: {net_recv_total_mb:.1f} MB)")

            # Process table
            proc_table = Table(box=box.SIMPLE, show_header=True, header_style="bold yellow")
            proc_table.add_column("PID", style="yellow", width=8)
            proc_table.add_column("Process", width=20)
            proc_table.add_column("CPU %", width=8)
            proc_table.add_column("RAM %", width=8)
            for p in processes:
                proc_table.add_row(
                    str(p.info['pid']),
                    p.info['name'][:18],
                    f"{p.info['cpu_percent']:.1f}",
                    f"{p.info['memory_percent']:.1f}"
                )

            # Benchmark panel
            bench_table = get_latest_benchmark()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content = Group(
                Columns([cpu_table, mem_table]),
                Columns([proc_table, bench_table]),
            )
            final = Panel(
                content,
                title=f"[bold green] System Monitor [/bold green] — [dim]{timestamp}[/dim]",
                subtitle="[dim]Ctrl+C to exit | refreshes every 0.5s[/dim]",
                border_style="green"
            )
            live.update(final)
