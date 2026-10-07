#!/usr/bin/env python3
"""Emit a bounded, structured rasp2 host-health sample to persistent journal."""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path


STATE_FILE = Path.home() / ".local/state/rasp2-host-monitor/state.json"


def read_text(path: str, default: str = "") -> str:
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        return default


def pressure(kind: str) -> dict:
    result: dict[str, float] = {}
    for line in read_text(f"/proc/pressure/{kind}").splitlines():
        fields = line.split()
        if not fields:
            continue
        prefix = fields[0]
        for field in fields[1:]:
            key, value = field.split("=", 1)
            if key in {"avg10", "avg60"}:
                result[f"{prefix}_{key}"] = float(value)
    return result


def meminfo() -> dict:
    values = {}
    for line in read_text("/proc/meminfo").splitlines():
        key, raw = line.split(":", 1)
        values[key] = int(raw.strip().split()[0]) * 1024
    return {
        "total": values.get("MemTotal", 0),
        "available": values.get("MemAvailable", 0),
        "swap_total": values.get("SwapTotal", 0),
        "swap_free": values.get("SwapFree", 0),
    }


def command(*args: str) -> str:
    try:
        return subprocess.run(args, text=True, capture_output=True, timeout=3, check=False).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def tcp_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def container_states() -> dict:
    states = {}
    for name in ("jellyfin", "alist", "rclone", "music-assistant"):
        value = command("docker", "inspect", "-f", "{{.State.Status}}", name)
        states[name] = value or "missing"
    return states


def main() -> int:
    now = int(time.time())
    boot_id = read_text("/proc/sys/kernel/random/boot_id")
    previous = {}
    try:
        previous = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass

    disk = shutil.disk_usage("/")
    memory = meminfo()
    load = os.getloadavg()
    temp_raw = read_text("/sys/class/thermal/thermal_zone0/temp", "0")
    sample = {
        "event": "rasp2_host_health",
        "ts": now,
        "boot_id": boot_id,
        "new_boot": bool(previous.get("boot_id") and previous.get("boot_id") != boot_id),
        "previous_last_seen": previous.get("last_seen"),
        "uptime_seconds": float(read_text("/proc/uptime", "0").split()[0]),
        "load_1m": round(load[0], 2),
        "load_5m": round(load[1], 2),
        "load_15m": round(load[2], 2),
        "memory_available": memory["available"],
        "memory_total": memory["total"],
        "swap_used": memory["swap_total"] - memory["swap_free"],
        "disk_used_percent": round((disk.used / disk.total) * 100, 1),
        "disk_free": disk.free,
        "temperature_c": round(int(temp_raw) / 1000, 1),
        "throttled": command("vcgencmd", "get_throttled"),
        "containers": container_states(),
        "ports": {
            "jellyfin_8096": tcp_open(8096),
            "alist_5244": tcp_open(5244),
            "music_assistant_8095": tcp_open(8095),
            "download_manager_8788": tcp_open(8788),
        },
        "cpu_pressure": pressure("cpu"),
        "memory_pressure": pressure("memory"),
        "io_pressure": pressure("io"),
    }
    print(json.dumps(sample, ensure_ascii=False, separators=(",", ":")), flush=True)

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"boot_id": boot_id, "last_seen": now}), encoding="utf-8")
    tmp.replace(STATE_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
