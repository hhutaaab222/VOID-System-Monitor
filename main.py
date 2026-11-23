#!/usr/bin/env python3
"""VOID System Monitor - cross-platform terminal system monitor.

Supported platforms: Linux, Windows and macOS.
Install dependency: python -m pip install psutil
"""

from __future__ import annotations

import csv
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import psutil

RED = "\033[31m"
GREEN = "\033[32m"
WHITE = "\033[37m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
YELLOW = "\033[33m"
ORANGE = "\033[38;5;208m"

ANSI_RE = re.compile(r"\033\[[0-?]*[ -/]*[@-~]")
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "void_config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "refresh_interval": 1.0,
    "process_count": 5,
    "bar_width": 20,
    "show_gpu": True,
    "show_temperature": True,
    "show_per_core": True,
    "show_processes": True,
}

def load_config() -> dict[str, Any]:
    """Load settings, creating a default config file on first launch."""
    config = DEFAULT_CONFIG.copy()

    if not CONFIG_PATH.exists():
        try:
            CONFIG_PATH.write_text(
                json.dumps(DEFAULT_CONFIG, indent=4) + "\n", encoding="utf-8"
            )
        except OSError:
            pass
        return config

    try:
        user_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(user_config, dict):
            config.update(user_config)
    except (OSError, json.JSONDecodeError):
        return config

    try:
        config["refresh_interval"] = max(0.2, min(30.0, float(config["refresh_interval"])))
    except (TypeError, ValueError):
        config["refresh_interval"] = DEFAULT_CONFIG["refresh_interval"]

    try:
        config["process_count"] = max(1, min(20, int(config["process_count"])))
    except (TypeError, ValueError):
        config["process_count"] = DEFAULT_CONFIG["process_count"]

    try:
        config["bar_width"] = max(8, min(40, int(config["bar_width"])))
    except (TypeError, ValueError):
        config["bar_width"] = DEFAULT_CONFIG["bar_width"]

    for key in ("show_gpu", "show_temperature", "show_per_core", "show_processes"):
        config[key] = bool(config.get(key, DEFAULT_CONFIG[key]))

    return config

def enable_ansi_colors() -> None:
    """Enable ANSI escape sequences in modern Windows terminals."""
    if platform.system() != "Windows":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        stdout_handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(stdout_handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(stdout_handle, mode.value | 0x0004)
    except Exception:
        # The monitor remains usable even if ANSI color enabling fails.
        pass


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=(100, 32))
    return max(40, size.columns), max(12, size.lines)


def visible_length(value: str) -> int:
    return len(ANSI_RE.sub("", value))


def section(title: str) -> str:
    return f"{BOLD}{GREEN}┌─ {title} {'─' * max(2, 34 - len(title))}{RESET}"


def make_bar(value: float, width: int = 20) -> str:
    value = max(0.0, min(100.0, float(value)))
    filled = int(round(width * value / 100))
    return f"{GREEN}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}"


def fit_text(value: str, width: int) -> str:
    """Trim ordinary display text to a fixed visible width."""
    if width <= 0:
        return ""
    plain = ANSI_RE.sub("", value)
    if len(plain) <= width:
        return value
    return plain[: max(0, width - 1)] + "…"


def combine_columns(left: list[str], right: list[str], width: int) -> list[str]:
    gap = 3
    column_width = max(20, (width - gap) // 2)
    result: list[str] = []
    for index in range(max(len(left), len(right))):
        left_line = left[index] if index < len(left) else ""
        right_line = right[index] if index < len(right) else ""
        left_visible = visible_length(left_line)
        if left_visible > column_width:
            left_line = fit_text(left_line, column_width)
            left_visible = visible_length(left_line)
        padding = " " * max(1, column_width - left_visible)
        result.append(f"{left_line}{padding}{' ' * gap}{right_line}")
    return result


def clear_frame() -> None:
    print("\033[H\033[2J", end="")

def get_system_info() -> list[str]:
    return [
        section("SYSTEM INFORMATION"),
        f"{BOLD}OS             :{RESET} {platform.system()} {platform.release()}",
        f"{BOLD}ARCHITECTURE   :{RESET} {platform.machine() or 'N/A'}",
        f"{BOLD}HOSTNAME       :{RESET} {platform.node() or 'N/A'}",
        f"{BOLD}PYTHON         :{RESET} {platform.python_version()}",
    ]


def get_cpu_info_lines() -> list[str]:
    physical = psutil.cpu_count(logical=False) or "N/A"
    logical = psutil.cpu_count(logical=True) or "N/A"
    frequency = psutil.cpu_freq()
    freq_text = f"{frequency.current:.0f} MHz" if frequency else "N/A"
    return [
        section("CPU INFORMATION"),
        f"{BOLD}PHYSICAL CORES :{RESET} {physical}",
        f"{BOLD}LOGICAL THREADS:{RESET} {logical}",
        f"{BOLD}CPU FREQUENCY  :{RESET} {freq_text}",
    ]

def get_cpu_temperature() -> float | None:
    """Return a likely CPU/package temperature where the OS exposes sensors.

    psutil generally exposes these sensors on Linux. Windows and macOS commonly
    return no CPU temperature through psutil, so N/A is an expected result.
    """
    sensor_function = getattr(psutil, "sensors_temperatures", None)
    if not callable(sensor_function):
        return None

    try:
        sensors = sensor_function(fahrenheit=False)
    except (OSError, NotImplementedError, RuntimeError):
        return None
    except Exception:
        return None

    if not sensors:
        return None

    preferred_keys = (
        "coretemp", "k10temp", "zenpower", "cpu_thermal", "soc_thermal",
        "cpu-thermal", "acpitz",
    )
    candidates: list[tuple[str, str, float]] = []
    for chip, entries in sensors.items():
        for entry in entries:
            current = getattr(entry, "current", None)
            if current is None:
                continue
            label = (getattr(entry, "label", "") or "").lower()
            candidates.append((chip.lower(), label, float(current)))

    for preferred in preferred_keys:
        matching = [item for item in candidates if preferred in item[0]]
        if matching:
            package = [item for item in matching if any(x in item[1] for x in ("package", "tdie", "tctl", "cpu"))]
            return (package or matching)[0][2]

    label_matches = [item for item in candidates if any(x in item[1] for x in ("package", "cpu", "tdie", "tctl"))]
    if label_matches:
        return label_matches[0][2]
    return None


def get_temperature_status(temp: float) -> tuple[str, str, str | None]:
    if temp < 60:
        return GREEN, "NORMAL", None
    if temp < 75:
        return YELLOW, "WARM", None
    if temp <= 84:
        return ORANGE, "HIGH", "WARNING: HIGH TEMPERATURE"
    return RED, "CRITICAL", "CRITICAL: CPU OVERHEATING"

def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=None)


def get_cpu_cores() -> list[float]:
    return psutil.cpu_percent(interval=None, percpu=True)


def get_ram_info() -> tuple[float, float, float]:
    memory = psutil.virtual_memory()
    used_mb = memory.used / (1024 ** 2)
    total_mb = memory.total / (1024 ** 2)
    return memory.percent, used_mb, total_mb


def get_disk_info() -> list[dict[str, Any]]:
    """Return usage for every mounted, accessible disk/partition."""
    disks: list[dict[str, Any]] = []
    seen_mountpoints: set[str] = set()

    try:
        partitions = psutil.disk_partitions(all=False)
    except Exception:
        partitions = []

    if not partitions:
        fallback = Path.home().anchor or ("C:\\" if platform.system() == "Windows" else "/")
        partitions = [type("Partition", (), {"device": fallback, "mountpoint": fallback, "fstype": ""})()]

    for partition in partitions:
        mountpoint = getattr(partition, "mountpoint", "")
        device = getattr(partition, "device", "")
        if not mountpoint:
            continue
        normalized = os.path.normcase(os.path.normpath(mountpoint))
        if normalized in seen_mountpoints:
            continue
        seen_mountpoints.add(normalized)

        try:
            usage = psutil.disk_usage(mountpoint)
        except (PermissionError, OSError):
            continue
        except Exception:
            continue

        disks.append({
            "device": device or mountpoint,
            "mountpoint": mountpoint,
            "total_gb": usage.total / (1024 ** 3),
            "used_gb": usage.used / (1024 ** 3),
            "free_gb": usage.free / (1024 ** 3),
            "percent": float(usage.percent),
        })

    if platform.system() == "Windows":
        disks.sort(key=lambda disk: (not disk["mountpoint"].lower().startswith("c:"), disk["mountpoint"].lower()))
    else:
        disks.sort(key=lambda disk: (disk["mountpoint"] != "/", disk["mountpoint"]))
    return disks


def get_top_processes(limit: int) -> list[dict[str, Any]]:
    processes: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            info = proc.info
            memory_info = info.get("memory_info")
            if memory_info is None:
                continue
            processes.append({
                "pid": info.get("pid", 0),
                "name": info.get("name") or "Unknown",
                "ram_mb": memory_info.rss / (1024 ** 2),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
            continue
        except Exception:
            continue
    processes.sort(key=lambda item: item["ram_mb"], reverse=True)
    return processes[:limit]

def get_gpu_info() -> list[dict[str, Any]]:
    if shutil.which("nvidia-smi") is None:
        return []

    command = [
        "nvidia-smi",
        "--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=2, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    if result.returncode != 0:
        return []

    gpus: list[dict[str, Any]] = []
    try:
        for row in csv.reader(result.stdout.strip().splitlines()):
            if len(row) < 5:
                continue
            name = row[0].strip()
            try:
                usage = float(row[1].strip())
                temperature = float(row[2].strip())
                memory_used = float(row[3].strip())
                memory_total = float(row[4].strip())
            except ValueError:
                continue
            gpus.append({
                "name": name,
                "usage": usage,
                "temperature": temperature,
                "memory_used": memory_used,
                "memory_total": memory_total,
            })
    except Exception:
        return []
    return gpus

class NetworkMonitor:
    def __init__(self) -> None:
        self.previous = psutil.net_io_counters()
        self.previous_time = time.monotonic()

    def sample(self) -> tuple[float, float, int, int]:
        current = psutil.net_io_counters()
        current_time = time.monotonic()
        elapsed = max(current_time - self.previous_time, 0.000001)

        if current is None or self.previous is None:
            download = upload = 0.0
            received_total = sent_total = 0
        else:
            received_delta = max(0, current.bytes_recv - self.previous.bytes_recv)
            sent_delta = max(0, current.bytes_sent - self.previous.bytes_sent)
            download = received_delta / elapsed / (1024 ** 2)
            upload = sent_delta / elapsed / (1024 ** 2)
            received_total = current.bytes_recv
            sent_total = current.bytes_sent

        self.previous = current
        self.previous_time = current_time
        return download, upload, sent_total, received_total

def build_header(width: int) -> list[str]:
    title = "V O I D   //   S Y S T E M   M O N I T O R"
    line = "═" * min(width, max(40, len(title) + 8))
    return [
        f"{BOLD}{GREEN}{line}{RESET}",
        f"{BOLD}{GREEN}{title:^{min(width, max(40, len(title) + 8))}}{RESET}",
        f"{BOLD}{GREEN}{line}{RESET}",
    ]


def build_left_panel(config: dict[str, Any], column_width: int) -> list[str]:
    lines: list[str] = []
    bar_width = max(8, min(int(config["bar_width"]), column_width - 28))

    lines.extend(get_system_info())
    lines.append("")
    lines.extend(get_cpu_info_lines())
    lines.append("")

    cpu = get_cpu_usage()
    lines.append(section("CPU LOAD"))
    lines.append(f"{BOLD}CPU USAGE :{RESET} {GREEN}{cpu:5.1f}%{RESET}  {make_bar(cpu, bar_width)}")

    ram_percent, ram_used, ram_total = get_ram_info()
    lines.append(f"{BOLD}RAM USAGE :{RESET} {GREEN}{ram_percent:5.1f}%{RESET}  {make_bar(ram_percent, bar_width)}")
    lines.append(f"{DIM}{ram_used:,.0f} MB / {ram_total:,.0f} MB{RESET}")

    if config["show_temperature"]:
        temp = get_cpu_temperature()
        if temp is None:
            lines.append(f"{BOLD}CPU TEMP  :{RESET} N/A {DIM}(sensor unavailable on this system){RESET}")
        else:
            color, status, warning = get_temperature_status(temp)
            lines.append(f"{BOLD}CPU TEMP  :{RESET} {color}{temp:.1f}°C [{status}]{RESET}")
            if warning:
                lines.append(f"{color}{warning}{RESET}")

    lines.append("")
    lines.append(section("DISK MONITOR"))
    disks = get_disk_info()
    if not disks:
        lines.append(f"{YELLOW}No accessible mounted disks found{RESET}")
    else:
        for disk in disks:
            mount = fit_text(disk["mountpoint"], max(10, column_width - 26))
            lines.append(f"{BOLD}{mount}{RESET}  {disk['used_gb']:.1f}/{disk['total_gb']:.1f} GB  {disk['percent']:.0f}%")
            lines.append(f"  {make_bar(disk['percent'], bar_width)}  {DIM}free {disk['free_gb']:.1f} GB{RESET}")

    if config["show_per_core"]:
        lines.append("")
        lines.append(section("CPU CORES"))
        cores = get_cpu_cores()
        for index, value in enumerate(cores, start=1):
            lines.append(f"CORE {index:02d}  {GREEN}{value:5.1f}%{RESET}  {make_bar(value, max(8, bar_width - 3))}")

    return lines


def build_right_panel(config: dict[str, Any], network: NetworkMonitor, column_width: int) -> list[str]:
    lines: list[str] = []

    if config["show_gpu"]:
        lines.append(section("GPU MONITOR"))
        gpus = get_gpu_info()
        if not gpus:
            lines.append(f"{DIM}NVIDIA GPU / nvidia-smi not detected{RESET}")
        else:
            for index, gpu in enumerate(gpus, start=1):
                lines.append(f"{BOLD}GPU {index}: {fit_text(gpu['name'], column_width - 8)}{RESET}")
                lines.append(f"USAGE       : {GREEN}{gpu['usage']:.0f}%{RESET}")
                lines.append(f"TEMPERATURE : {GREEN}{gpu['temperature']:.0f}°C{RESET}")
                lines.append(f"VRAM        : {GREEN}{gpu['memory_used']:.0f} / {gpu['memory_total']:.0f} MB{RESET}")
                if index < len(gpus):
                    lines.append("")

    lines.append("")
    download, upload, sent_total, received_total = network.sample()
    lines.append(section("NETWORK MONITOR"))
    lines.append(f"{BOLD}DOWNLOAD SPEED :{RESET} {GREEN}{download:8.2f} MB/s{RESET}")
    lines.append(f"{BOLD}UPLOAD SPEED   :{RESET} {GREEN}{upload:8.2f} MB/s{RESET}")
    lines.append(f"{DIM}Received total : {received_total / (1024 ** 2):,.1f} MB{RESET}")
    lines.append(f"{DIM}Sent total     : {sent_total / (1024 ** 2):,.1f} MB{RESET}")

    if config["show_processes"]:
        lines.append("")
        lines.append(section("TOP PROCESSES / RAM"))
        processes = get_top_processes(int(config["process_count"]))
        if not processes:
            lines.append(f"{DIM}No process information available{RESET}")
        else:
            lines.append(f"{DIM}{'PROCESS':<22} {'PID':>8} {'RAM':>9}{RESET}")
            for process in processes:
                name = fit_text(str(process["name"]), 21)
                lines.append(
                    f"{name:<22} {process['pid']:>8} {GREEN}{process['ram_mb']:>7.1f} MB{RESET}"
                )

    return lines


def render_monitor(config: dict[str, Any], network: NetworkMonitor) -> None:
    width, _ = terminal_size()
    clear_frame()
    print("\n".join(build_header(width)))
    print()

    column_width = (width - 5) // 2
    left = build_left_panel(config, column_width)
    right = build_right_panel(config, network, column_width)

    if width >= 100:
        frame_lines = combine_columns(left, right, width)
    else:
        frame_lines = left + ["", f"{BOLD}{GREEN}──────────── NETWORK / GPU / PROCESSES ────────────{RESET}"] + right

    print("\n".join(frame_lines))
    print()
    print(
        f"{DIM}Refresh: {config['refresh_interval']:.1f}s  |  "
        f"Edit {CONFIG_PATH.name} to change settings  |  CTRL+C to exit{RESET}"
    )
    sys.stdout.flush()

def main() -> None:
    enable_ansi_colors()
    config = load_config()

    psutil.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None, percpu=True)
    network = NetworkMonitor()

    try:
        print("\033[?25l", end="")
        while True:
            render_monitor(config, network)
            time.sleep(config["refresh_interval"])
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\033[?25h{RESET}")
        print(f"{GREEN}VOID monitor stopped.{RESET}")


if __name__ == "__main__":
    main()
