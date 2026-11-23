import os
import time
import platform
import subprocess
from psutil import cpu_percent
from psutil import virtual_memory
from psutil import cpu_count
from psutil import cpu_freq
from psutil import disk_usage
from psutil import sensors_temperatures
from psutil import process_iter
from psutil import net_io_counters

RED = "\033[31m"
GREEN = "\033[32m"
WHITE = "\033[37m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
YELLOW = "\033[33m"
ORANGE = "\033[38;5;208m"



def clear_screen():
    os_name = platform.system()
    if os_name == "Windows":
        os.system("cls")
    elif os_name == "Linux":
        os.system("clear")

def get_disk_info():
    disk_plaform = platform.system()
    
    if disk_plaform == "Windows":
        disk = disk_usage("\\")
    elif disk_plaform == "Linux":
        disk = disk_usage("/")

    disk_total = round(disk.total / (1024 ** 3), 2)
    disk_used = round(disk.used / (1024 ** 3), 2)
    disk_free = round(disk.free / (1024 ** 3), 2)
    disk_percent = disk.percent
    return disk_total, disk_used, disk_free, disk_percent

def get_system_info():
    oc = platform.system()
    release = platform.release()
    machine = platform.machine()
    hostname = platform.node()
    print(f"{BOLD}{GREEN}SYSTEM INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}os{RESET}             : {oc}\n"
    f"{BOLD}{GREEN}kernel{RESET}         : {release}\n"
    f"{BOLD}{GREEN}architecture{RESET}   : {machine}\n"
    f"{GREEN}{BOLD}hostname{RESET}       : {hostname}"
    )

def get_network_info():
    network = net_io_counters()
    sent = round(network.bytes_sent / (1024 ** 2), 2)
    received = round(network.bytes_recv / (1024 ** 2), 2)
    return sent, received

def get_upload_speed():
    sent, received = get_network_info()
    old_value = sent
    time_speed1 = time.time()
    time.sleep(1)
    sent, received = get_network_info()
    new_value = sent
    time_speed2 = time.time()
    difference = new_value - old_value
    past_time = time_speed2 - time_speed1
    division_of_time = difference / past_time
    upload_speed = division_of_time / 1024 ** 2
    return upload_speed

def get_download_speed():
    sent, received = get_network_info()
    old_value = received
    time_speed1 = time.time()
    time.sleep(1)
    sent, received = get_network_info()
    new_value = received
    time_speed2 = time.time()
    difference = new_value - old_value
    past_time = time_speed2 - time_speed1
    division_of_time = difference / past_time
    download_speed = division_of_time / 1024 ** 2
    return download_speed

def get_cpu_temp():
    try:
        temps = sensors_temperatures()
        cpu_temp = temps.get("coretemp", [])
        
        for i in cpu_temp:
            if i.label == "Package id 0":
                return i.current

        return None
    except Exception:
        return None

def get_temp_warning(temp):
    if temp <= 75:
        return None
    elif temp <=84:
        return ORANGE, "WARNING: HIGH TEMPERATURE"
    else:
        return RED, "CRITICAL: CPU OVERHEATING" 



def get_temp_color(temp):
    if temp < 60:
        return GREEN, "NORMAL"
    elif temp < 75:
        return YELLOW, "WARM"
    elif temp <= 84:
        return ORANGE, "HIGH"
    else:
        return RED, "CRITICAL"

def get_top_processes():
    processes = []

    for proc in process_iter(["pid", "name", "memory_info"]):
        info = proc.info

        processes.append({
            "pid": info["pid"],
            "name": info["name"],
            "ram": info["memory_info"].rss
        })
    processes.sort(key=lambda x: x["ram"], reverse=True)
    
    
    return processes[:5]

def get_cpu_info():
    fiz_yadro = cpu_count(logical=False)
    log_potoki = cpu_count(logical=True)
    freq_cpu = round(cpu_freq().current)
    
    print(f"\n{BOLD}{GREEN}CPU INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}physical cores{RESET}    :{fiz_yadro}\n"
    f"{BOLD}{GREEN}Logical threads{RESET}   :{log_potoki}\n"
    f"{BOLD}{GREEN}CPU frequency{RESET}     :{freq_cpu}MHz\n"
    )

def get_cpu_cores():
    cpu_workload = cpu_percent(interval=None, percpu=True)
    return cpu_workload

def get_gpu_info():
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("GPU ERROR:", result.stderr)
        return None
    return result.stdout.strip()
    print(get_gpu_info())

def pause():
    input(BOLD + GREEN + f"\npress ENTER to see the load in real time ...\n" + RESET)

def render_monitor():
    print("\033[2J\033[H", end="")
    cpu1 = get_cpu()
    print(f"{BOLD}CPU USAGE: {RESET}{GREEN}{cpu1}%{RESET}")
    make_bar(cpu1)
    
    ram1 = get_ram()
    print(f"\n{BOLD}RAM USAGE: {RESET}{GREEN}{ram1}%{RESET}")
    make_bar(ram1)
    
    total, used, free, percent = get_disk_info()
    print(f"\n{BOLD}DISK USAGE: {RESET}{GREEN}{used} GB / {total} GB — {percent} %")
    make_bar(percent)
    
    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        color, status = get_temp_color(cpu_temp)
        print(f"\n{BOLD}CPU TEMPERATURE: {RESET}{GREEN}{cpu_temp}°C{RESET} [{color}{status}{RESET}]")
    
        warning = get_temp_warning(cpu_temp)

        if warning is not None:
            color1, status1 = warning
            print(f"{color1}{status1}{RESET}")
    
    else:
        print(f"\n{BOLD}CPU TEMPERATURE: {RESET}N/A")
    
    print(f"\n{BOLD}TOP PROCESSES:{RESET}")
    for proc in get_top_processes():
        print(
            f"{proc['name']:<20} "
            f"PID:{GREEN}{proc['pid']:<8}{RESET} "
            f"RAM:{GREEN}{round(proc['ram'] / 1024**2, 2)} MB{RESET}"
        )

    gpu = get_gpu_info()
    gpu_data = gpu.split(",")
    gpu_usage, gpu_temp, vram_used, vram_total = map(int, gpu_data)

    print(f"\n{BOLD}GPU INFORMATION:{RESET}\n"
        f"{BOLD}GPU USAGE       : {RESET}{GREEN}{gpu_usage}{RESET}\n"
        f"{BOLD}GPU TEMPERATURE : {RESET}{GREEN}{gpu_temp}{RESET}\n"
        f"{BOLD}VRAM            : {RESET}{GREEN}{vram_used} / {vram_total}{RESET}"
        )

    print()
    cpuworkloadsave = get_cpu_cores()
    print(BOLD + f"CPU CORES:{RESET}")
    for index, value in enumerate(cpuworkloadsave, start=1):
        print(f"CPU CORE {index} - {RESET}{GREEN}{value:.1f}%{RESET}")
        make_bar(value)


    download = get_download_speed()
    upload = get_upload_speed()
    print(BOLD + "\n       NETWORK MONITOR:" + RESET)
    print(BOLD + f"DOWNLOAD SPEED    :{RESET}{GREEN}{download:.2f} MB/s{RESET}\n"
    f"{BOLD}UPLOAD SPEED      :{RESET}{GREEN}{upload:.2f} MB/s{RESET}"
    )
    
def show_header():
    clear_screen()
    art0 = r"""
██╗   ██╗ ██████╗ ██╗██████╗ ███████╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
██║   ██║██╔═══██╗██║██╔══██╗██╔════╝    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
██║   ██║██║   ██║██║██║  ██║█████╗      ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
╚██╗ ██╔╝██║   ██║██║██║  ██║██╔══╝      ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝███████╗    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝ ╚══════╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
                                         [ M O N I T O R ]
    """
    print(GREEN + art0 + RESET)
    time.sleep(1)
show_header()
get_system_info()
get_cpu_info()
total, used, free, percent = get_disk_info()
gpu = get_gpu_info()
gpu_data = gpu.split(",")
gpu_usage, gpu_temp, vram_used, vram_total = gpu_data
gpu_usage, gpu_temp, vram_used, vram_total = map(int, gpu_data)

print(f"{BOLD}{GREEN}GPU INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}GPU USAGE       : {RESET}{gpu_usage}\n"
    f"{BOLD}{GREEN}GPU TEMPERATURE : {RESET}{gpu_temp}\n"
    f"{BOLD}{GREEN}VRAM            : {RESET}{vram_used} / {vram_total}"
    )

print(f"\n{BOLD}{GREEN}DISK INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}total    :{RESET}{total} GB\n"
    f"{BOLD}{GREEN}used     :{RESET}{used} GB\n"
    f"{BOLD}{GREEN}free     :{RESET}{free} GB\n"
    f"{BOLD}{GREEN}percent  :{RESET}{percent}%\n"
)

def get_cpu():
    cpu = cpu_percent(interval=None)
    return cpu

    
def make_bar(cpu1):
    filled = int(30 * cpu1 / 100)
    empty = 30 - filled
    print(GREEN + "█" * filled + RESET + "░" * empty)


def get_ram():
    ram = virtual_memory()
    return ram.percent
cpu_percent(interval=None)
cpu_percent(interval=None, percpu=True)     

pause()
while True:
    render_monitor()
    time.sleep(1)
    
