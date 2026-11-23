# VOID System Monitor

A lightweight, cross-platform system monitor for the terminal, built with Python and [psutil](https://github.com/giampaolo/psutil). VOID uses a dark terminal layout with neon-green accents and live system statistics.

**Supported platforms:** Linux, Windows, and macOS  
**Main dependency:** `psutil`

---

## Features

- **System information** — operating system, kernel/release, architecture, hostname, and Python version.
- **CPU monitoring** — overall CPU usage, physical and logical core counts, current frequency, and per-core usage.
- **CPU temperature** — temperature status indicators and high-temperature warnings when sensor data is available.
- **Memory monitoring** — RAM usage percentage and used/total memory.
- **Multi-disk monitoring** — usage, free space, and capacity for accessible mounted disks and partitions.
- **GPU monitoring** — NVIDIA GPU name, utilization, temperature, and VRAM usage through `nvidia-smi`.
- **Network monitoring** — live download and upload rates, plus cumulative sent and received data.
- **Process monitoring** — the top memory-consuming processes, including process name, PID, and RAM usage.
- **Adaptive terminal layout** — two columns on wider terminals and a vertically stacked layout on narrower terminals.
- **Configurable refresh interval** — choose how often the dashboard updates.
- **JSON configuration** — enable or disable dashboard sections and adjust display settings.

## Preview

VOID is designed for a terminal with ANSI color support. The interface uses green highlights, colored usage bars, and compact system-information panels.

---

## Requirements

- Python **3.10 or newer**.
- A terminal emulator with ANSI escape-sequence support.
- `psutil` (installed from `requirements.txt`).
- For NVIDIA GPU statistics: working NVIDIA drivers and the `nvidia-smi` command available in `PATH`.

Most monitoring features work without administrator/root privileges. Some process or disk information may be unavailable when the operating system restricts access.

## Installation

### Linux (including Arch Linux)

Clone or download the project, then open a terminal in the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Arch Linux, install Python if it is not already available:

```bash
sudo pacman -S python
```

### macOS

Open Terminal in the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

Open PowerShell in the project directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, you can run the environment's Python directly instead:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

With the virtual environment activated:

```bash
python main.py
```

On Windows, the same command works after activating `.venv`. You can also run:

```powershell
.venv\Scripts\python.exe main.py
```

Press **Ctrl+C** to stop VOID and return to the shell.

---

## Configuration

VOID reads `void_config.json` from the same directory as `main.py`. If the file does not exist, VOID creates it with default settings on the first launch.

Default configuration:

```json
{
    "refresh_interval": 1.0,
    "process_count": 5,
    "bar_width": 20,
    "show_gpu": true,
    "show_temperature": true,
    "show_per_core": true,
    "show_processes": true
}
```

| Setting | Default | Description | Accepted values |
|---|---:|---|---|
| `refresh_interval` | `1.0` | Time between dashboard updates, in seconds. | `0.2`–`30.0` |
| `process_count` | `5` | Number of top RAM-consuming processes to display. | `1`–`20` |
| `bar_width` | `20` | Width of CPU, RAM, and disk usage bars. | `8`–`40` |
| `show_gpu` | `true` | Show the GPU panel. | `true` / `false` |
| `show_temperature` | `true` | Show CPU temperature when available. | `true` / `false` |
| `show_per_core` | `true` | Show per-core CPU usage. | `true` / `false` |
| `show_processes` | `true` | Show the top memory-consuming processes. | `true` / `false` |

After changing the configuration, restart VOID for the new settings to take effect. Invalid or out-of-range numeric values are replaced with safe defaults or clamped to the supported range.

---

## Platform notes and limitations

| Feature | Linux | Windows | macOS |
|---|---|---|---|
| CPU usage and per-core usage | Supported | Supported | Supported |
| RAM usage | Supported | Supported | Supported |
| Disk usage | Accessible mounted disks | Accessible mounted volumes | Accessible mounted volumes |
| Process list | Supported; permissions may limit details | Supported; permissions may limit details | Supported; permissions may limit details |
| Network rates and totals | Supported | Supported | Supported |
| CPU temperature | Depends on available sensors | Often unavailable through `psutil` | Often unavailable through `psutil` |
| NVIDIA GPU statistics | Requires `nvidia-smi` | Requires `nvidia-smi` | Only where NVIDIA hardware and the utility are supported |

### CPU temperature

Temperature readings depend on sensor access provided by the operating system and hardware. Linux systems commonly expose sensors through kernel hardware-monitoring interfaces. On Windows and macOS, VOID may show `N/A`; this is expected when `psutil` cannot access a compatible sensor.

Temperature status thresholds used by VOID:

- Below `60°C` — **NORMAL**
- `60°C` to below `75°C` — **WARM**
- `75°C` to `84°C` — **HIGH** (warning)
- Above `84°C` — **CRITICAL** (overheating warning)

These are display thresholds, not a replacement for the temperature limits specified by your CPU manufacturer.

### GPU monitoring

GPU statistics are currently collected only through NVIDIA's `nvidia-smi`. VOID does not currently provide native AMD or Intel GPU monitoring. If `nvidia-smi` is missing, the GPU panel displays an unavailable message and the rest of the monitor continues to work.

### Terminal width

On terminals at least 100 columns wide, the dashboard uses a two-column layout. On narrower terminals, the panels are stacked vertically. Increase the terminal width for the full side-by-side layout.

---

## Project structure

```text
VOID-System-Monitor/
├── main.py             # Monitoring logic and terminal interface
├── requirements.txt    # Python dependencies
├── void_config.json    # User configuration (created if missing)
└── README.md           # Project documentation
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'psutil'`**

Activate the virtual environment and install the dependency:

```bash
python -m pip install -r requirements.txt
```

**The GPU panel says that `nvidia-smi` was not detected**

Check that NVIDIA drivers and NVIDIA system-management utilities are installed, then verify that `nvidia-smi` runs from the terminal and is available in `PATH`.

**CPU temperature shows `N/A`**

The current OS, hardware, or sensor configuration may not expose temperature data through `psutil`. Other monitoring panels should continue to work.

**Some disks or processes are missing**

The operating system may restrict access to certain mount points or process details. VOID skips entries it cannot read.

**The display looks cramped**

Widen the terminal window. VOID switches to its two-column layout when the terminal is at least 100 columns wide.

---

## License

No license file is currently included. Add a `LICENSE` file before distributing or reusing this project under a specific open-source license.
