import psutil
import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
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

def build_dashboard() -> Panel:
    # CPU
    cpu_total = psutil.cpu_percent(interval=0.1)
    cpu_cores = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_freq = psutil.cpu_freq()
    cpu_count = psutil.cpu_count()

    # RAM
    ram = psutil.virtual_memory()
    ram_used_gb = ram.used / 1024**3
    ram_total_gb = ram.total / 1024**3

    # Disk
    disk = psutil.disk_usage('/')
    disk_used_gb = disk.used / 1024**3
    disk_total_gb = disk.total / 1024**3
    disk_percent = disk.percent

    # Network
    net = psutil.net_io_counters()
    net_sent_mb = net.bytes_sent / 1024**2
    net_recv_mb = net.bytes_recv / 1024**2

    # Top processes by CPU
    processes = sorted(
        psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
        key=lambda p: p.info['cpu_percent'] or 0,
        reverse=True
    )[:5]

    # Build CPU table
    cpu_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    cpu_table.add_column("CPU Metrics", style="cyan", width=25)
    cpu_table.add_column("Value", width=35)
    cpu_table.add_row("Overall CPU", get_cpu_bar(cpu_total))
    cpu_table.add_row("Frequency", f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A")
    cpu_table.add_row("Core Count", str(cpu_count))
    for i, pct in enumerate(cpu_cores[:4]):
        cpu_table.add_row(f"Core {i}", get_cpu_bar(pct))

    # Build RAM/Disk table
    mem_table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
    mem_table.add_column("Memory & Disk", style="magenta", width=25)
    mem_table.add_column("Value", width=35)
    mem_table.add_row("RAM Usage", get_ram_bar(ram.percent, ram_used_gb, ram_total_gb))
    mem_table.add_row("RAM Free", f"{(ram.available / 1024**3):.1f} GB")
    mem_table.add_row("Disk Usage", get_ram_bar(disk_percent, disk_used_gb, disk_total_gb))
    mem_table.add_row("Disk Free", f"{(disk.free / 1024**3):.1f} GB")
    mem_table.add_row("Net Sent", f"{net_sent_mb:.1f} MB")
    mem_table.add_row("Net Recv", f"{net_recv_mb:.1f} MB")

    # Build process table
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

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    layout = Columns([cpu_table, mem_table])

    return Panel(
        Table.grid(
            padding=1,
            expand=True
        ),
        title=f"[bold green]System Monitor[/bold green] — [dim]{timestamp}[/dim]",
        subtitle="[dim]Press Ctrl+C to exit[/dim]",
        border_style="green"
    ), layout, proc_table

if __name__ == "__main__":
    print("Starting system monitor... Press Ctrl+C to exit\n")
    time.sleep(1)

    with Live(refresh_per_second=2, screen=True) as live:
        while True:
            panel, layout, proc_table = build_dashboard()

            from rich.console import Group
            content = Group(layout, proc_table)
            final = Panel(
                content,
                title="[bold green] System Monitor [/bold green]",
                subtitle="[dim]Ctrl+C to exit | refreshes every 0.5s[/dim]",
                border_style="green"
            )
            live.update(final)
            time.sleep(0.5)
