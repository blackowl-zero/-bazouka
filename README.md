# 🔫 bazouka
**BLE Security Research Tool** v1.5 stable

A personal project for exploring Bluetooth Low Energy behavior. Built for testing BLE devices in controlled environments — my own gear, my own lab.

---

## What it does

- Scans the area for nearby BLE devices and lists them in a clean table
- Attempts repeated connect/disconnect cycles on a target device
- Sends raw BLE advertising packets using `hcitool`

Nothing fancy, just a script I built to learn how BLE stacks behave under stress.

---

## Requirements

- Python 3.10+
- Linux with a working Bluetooth adapter (`hci0`)
- `hcitool` installed (usually part of `bluez`)
- The following Python packages:

## download 
```
git clone https://github.com/blackowl-zero/bazouka.git
```


```
bleak
rich
```

Install with:

```bash
pip install bleak rich
```

---

## Usage

```bash
sudo python3 bazouka.py
```

It'll scan for 30 seconds, show you a table of found devices, and then ask you to pick a target and choose what to do.

> Change the scan duration directly in the `scan_for_devices()` call at the bottom if 30s is too long/short.

---

## Modes

| Mode | What it does |
|------|-------------|
| `1` Disconnect Attack | Connects and disconnects repeatedly to a target |
| `2` BLE Flood | Sends raw advertising packets for a set duration |

---

## ⚠️ Legal / Ethical note

This tool is for **educational purposes and testing on devices you own or have explicit permission to test.**

Using this against third-party devices without authorization is illegal in most countries. Don't be stupid about it.

---

## Known issues / TODO

- No kill switch mid-attack (Ctrl+C works but it's ugly)
- `ble_flood` silently eats errors — needs better logging
- Tested only on Linux / `hci0` — no guarantees on other setups
- Input validation is minimal, will probably break if you're weird about it

---

## Why "bazouka"

Because why not.

---

*Built for learning. Use responsibly.*
