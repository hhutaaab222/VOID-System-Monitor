import os
import time
import platform
from psutil import cpu_percent
from psutil import virtual_memory
from psutil import cpu_count
from psutil import cpu_freq
from psutil import disk_usage
from psutil import sensors_temperatures
from psutil import process_iter

RED = "\033[31m"
GREEN = "\033[32m"
WHITE = "\033[37m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
def clear_screen():
    os_name = platform.system()
    if os_name == "Windows":
        os.system("cls")
    elif os_name == "Linux":
        os.system("clear")

def get_disk_info():
    disk_plaform = platform.system()
    
    if disk_plaform == "Windows":
        disk = disk_usage("C:\\")
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

def get_cpu_temp():
    temps = sensors_temperatures()
    cpu_temp = temps.get("coretemp", [])
    
    for i in cpu_temp:
        if i.label == "Package id 0":
            return i.current

    return None

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
    
    
    return processes[:10]

def get_cpu_info():
    fiz_yadro = cpu_count(logical=False)
    log_potoki = cpu_count(logical=True)
    freq_cpu = round(cpu_freq().current)
    
    print(f"\n{BOLD}{GREEN}CPU INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}physical cores{RESET}    :{fiz_yadro}\n"
    f"{BOLD}{GREEN}Logical threads{RESET}   :{log_potoki}\n"
    f"{BOLD}{GREEN}CPU frequency{RESET}     :{freq_cpu}MHz\n"
    )

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
        print(f"\n{BOLD}CPU TEMPERATURE: {RESET}{GREEN}{cpu_temp}°C")
    else:
        print(f"\n{BOLD}CPU TEMPERATURE: {RESET}N/A")
    
    print(f"\n{GREEN}{BOLD}------------------------------------------------")
    print(  f"{BOLD}             MONITORING PROCESSES               " + RESET)
    print(f"\n{BOLD}TOP PROCESSES:{RESET}")
    for proc in get_top_processes():
        print(
            f"{proc['name']:<20} "
            f"PID:{GREEN}{proc['pid']:<8}{RESET} "
            f"RAM:{GREEN}{round(proc['ram'] / 1024**2, 2)} MB{RESET}"
        )
    


def show_header():
    clear_screen()
    art0 = r"""
 ▄   ▄ ▄▄▄ ▄ ▄▄▄  ▄▄▄▄   ▄▄▄ ▄   ▄  ▄▄▄ ▄▄▄▄▄ ▄▄▄▄ ▄   ▄   ▄   ▄  ▄▄▄  ▄   ▄ ▄ ▄▄▄▄▄  ▄▄▄  ▄▄▄▄  
 █   █ █ █ █ █  █ █     █     ▀▄▀  █      █   █    ██ ██   ██ ██ █   █ ██  █ █   █   █   █ █   █ 
  █ █  █ █ █ █  █ █▀▀    ▀▀▀▄  █    ▀▀▀▄  █   █▀▀  █ █ █   █ █ █ █   █ █ █ █ █   █   █   █ ▄▄▄▄▀ 
   ▀   ▀▀▀ ▀ ▀▀▀  ▀▀▀▀  ▀▀▀▀   ▀   ▀▀▀▀   ▀   ▀▀▀▀ ▀   ▀   ▀   ▀  ▀▀▀  ▀  ██ ▀   ▀    ▀▀▀  ▀   ▀ 

                                            by Void Monitor
    """
    print(GREEN + art0 + RESET)
    time.sleep(1)
show_header()
get_system_info()
get_cpu_info()
total, used, free, percent = get_disk_info()


print(f"\n{BOLD}{GREEN}DISK INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}total    :{RESET}{total} GB\n"
    f"{BOLD}{GREEN}used     :{RESET}{used} GB\n"
    f"{BOLD}{GREEN}free     :{RESET}{free} GB\n"
    f"{BOLD}{GREEN}percent  :{RESET}{percent}%"
)

def get_cpu():
    cpu = cpu_percent(interval=1)
    return cpu

    
def make_bar(cpu1):
    filled = int(30 * cpu1 / 100)
    empty = 30 - filled
    print(GREEN + "█" * filled + RESET + "░" * empty)


def get_ram():
    ram = virtual_memory()
    return ram.percent

pause()
while True:
    render_monitor()
    time.sleep(0.05)
    
