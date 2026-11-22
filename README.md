# VOID System Monitor

<p align="center">
  <img src="https://img.shields.io/badge/VOID-SYSTEM_MONITOR-39FF14?style=for-the-badge&labelColor=0D0D0D">
  <img src="https://img.shields.io/badge/Python-3.10+-39FF14?style=for-the-badge&labelColor=0D0D0D">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-39FF14?style=for-the-badge&labelColor=0D0D0D">
</p>

<p align="center">
  <b>A lightweight terminal-based system monitor written in Python.</b>
</p>

<img width="1077" height="787" alt="image" src="https://github.com/user-attachments/assets/3f3108c5-cad8-4158-93e3-baea0a40121e" />




## About

**VOID** is a lightweight terminal-based system monitoring utility built with Python.

It provides real-time information about system resource usage, CPU characteristics, memory utilization, disk space and processor temperature — all inside a minimal terminal interface.

Designed with a dark aesthetic and neon green accents, VOID focuses on delivering essential system information without unnecessary complexity.

---

## Features

- **CPU Monitoring** — real-time CPU utilization
- **RAM Monitoring** — memory usage percentage
- **Disk Monitoring** — total, used and available disk space
- **CPU Temperature** — processor temperature monitoring through available sensors
- **System Information** — OS, kernel, architecture and hostname
- **CPU Information** — physical cores, logical threads and frequency
- **Live Monitoring** — continuously refreshed system statistics
- **Visual Usage Bars** — terminal-based resource indicators
- **Minimal Interface** — lightweight ANSI terminal UI

---

## Interface

VOID uses a minimal terminal interface built around:

- Dark terminal aesthetics
- Neon green color scheme
- ASCII branding
- Real-time system statistics
- Simple resource visualization

---

## Monitored Resources

| Resource | Information |
|---|---|
| CPU | Usage, physical cores, logical threads, frequency, temperature |
| RAM | Memory utilization |
| Disk | Total, used, free space, usage percentage |
| System | OS, kernel, architecture, hostname |

---

## Requirements

- Python 3.10+
- `psutil`
- Terminal with ANSI escape sequence support

---

## Installation

Clone the repository:

```bash
git clone https://github.com/hhutaaab222/VOID-System-Monitor.git
```

Enter the project directory:

```bash
cd VOID-System-Monitor
```

Install the dependency:

```bash
pip install psutil
```

---

## Usage

Run VOID:

```bash
python main.py
```

After initialization, VOID displays system information and disk statistics.

Press `ENTER` to enter real-time monitoring mode.

To exit the monitor:

```text
CTRL + C
```

---

## Technologies

| Technology | Purpose |
|---|---|
| Python | Core application |
| psutil | System resource monitoring |
| ANSI Escape Codes | Terminal colors and formatting |
| platform | OS and system information |
| os | Operating system interaction |

---

## Platform Support

| Feature | Linux | Windows |
|---|:---:|:---:|
| CPU Monitoring | ✓ | ✓ |
| RAM Monitoring | ✓ | ✓ |
| Disk Monitoring | ✓ | ✓ |
| System Information | ✓ | ✓ |
| CPU Information | ✓ | ✓ |
| CPU Temperature | Sensor dependent | Sensor dependent |

Hardware sensor availability depends on the operating system, drivers and hardware configuration.

---

## Roadmap

- [x] CPU temperature color indicators
- [X] Thermal warning system
- [ ] Per-core CPU monitoring
- [ ] GPU monitoring
- [ ] Network monitoring
- [x] Process monitoring
- [ ] Configurable refresh interval
- [ ] Multi-disk support
- [ ] Improved terminal interface
- [ ] Configuration system

---

## Philosophy

> No unnecessary noise. Just your system, its state, and the information that matters.

VOID is built around simplicity, clarity and a minimal terminal experience.

---

## Author

**VOID Project**

GitHub: [@hhutaaab222](https://github.com/hhutaaab222)

Repository: [VOID-System-Monitor](https://github.com/hhutaaab222/VOID-System-Monitor)

---

<p align="center">
  <code>MONITOR YOUR SYSTEM. KNOW WHAT RUNS.</code>
</p>
