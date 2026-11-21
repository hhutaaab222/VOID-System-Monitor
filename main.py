import os
import time
import platform
from psutil import cpu_percent
from psutil import virtual_memory
from psutil import cpu_count
from psutil import cpu_freq
from psutil import disk_usage

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
    input(WHITE + f"\npress ENTER to see the load in real time ...\n{WHITE}{DIM}update every 2 seconds" + RESET)

def show_header():
    clear_screen()
    art0 = r"""
██╗   ██╗ ██████╗ ██╗██████╗     ███╗   ███╗ ██████╗ ███╗   ██╗
██║   ██║██╔═══██╗██║██╔══██╗    ████╗ ████║██╔═══██╗████╗  ██║
██║   ██║██║   ██║██║██║  ██║    ██╔████╔██║██║   ██║██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║    ██║╚██╔╝██║██║   ██║██║╚██╗██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    """
    art1 = rf"""
╔════════════════════════════════════════════════════════════════╗
║                  {BOLD + GREEN}VOID{RESET}                ║
║             {WHITE}SYSTEM MONITOR{RESET}           ║
║         {DIM}LIVE SYSTEM DIAGNOSTICS{RESET}      ║
╚════════════════════════════════════════════════════════════════╝{RESET}"""
    print(GREEN + art0 + RESET)
    time.sleep(1)
    print(art1)
show_header()
get_system_info()
get_cpu_info()
total, used, free, percent = get_disk_info()

print(f"{BOLD}{GREEN}DISK INFORMATION:{RESET}\n"
    f"{BOLD}{GREEN}total    :{RESET}{total} GB\n"
    f"{BOLD}{GREEN}used     :{RESET}{used} GB\n"
    f"{BOLD}{GREEN}free     :{RESET}{free} GB\n"
    f"{BOLD}{GREEN}percent  :{RESET}{percent}%"
)

def get_cpu():
    cpu = cpu_percent(interval=1)
    return cpu
cpu_resualt = get_cpu()
print(f"\n{BOLD}CPU USAGE: {RESET}{GREEN}{cpu_resualt}%{RESET}")
    
def make_bar(cpu1):
    filled = int(30 * cpu1 / 100)
    empty = 30 - filled
    print(GREEN + "█" * filled + RESET + "░" * empty)

cpu = get_cpu()
make_bar(cpu)

def get_ram():
    ram = virtual_memory()
    return ram.percent
ram_resualt = get_ram()
print(WHITE + BOLD + "----------------------------------" + RESET)
print(f"{BOLD}RAM USAGE: {RESET}{GREEN}{ram_resualt}%{RESET}")
ram = get_ram()
make_bar(ram)
pause()

while True:
    clear_screen()
    cpu1 = get_cpu()
    print(f"{BOLD}CPU USAGE: {RESET}{GREEN}{cpu1}%{RESET}")
    make_bar(cpu1)
    ram1 = get_ram()
    print(f"\n{BOLD}RAM USAGE: {RESET}{GREEN}{ram1}%{RESET}")
    make_bar(ram1)
    total, used, free, percent = get_disk_info()
    print(f"\n{BOLD}DISK USAGE:\n{RESET}{used} GB / {total} GB — {percent} %")
    make_bar(percent)
    time.sleep(2)
    
