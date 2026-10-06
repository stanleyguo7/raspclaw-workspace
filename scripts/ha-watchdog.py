#!/usr/bin/env python3
"""Conservative external watchdog for the home Home Assistant instance.

The watchdog runs on rasp2, outside Home Assistant.  It only acts after three
consecutive failures and enforces per-action cooldowns.  Credentials remain in
the local token file and are never logged.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


HA_URL = os.environ.get("HA_URL", "http://192.168.3.254:8123")
TOKEN_FILE = Path(
    os.environ.get(
        "HA_TOKEN_FILE",
        "/home/guosq/.openclaw/.secrets/ha_persistent_token_siyi.key",
    )
)
STATE_FILE = Path(
    os.environ.get(
        "HA_WATCHDOG_STATE",
        "/home/guosq/.local/state/ha-watchdog/state.json",
    )
)
RASP_HOST = os.environ.get("HA_RASP_HOST", "guosq@192.168.3.254")
FAILURE_THRESHOLD = 3
ACTION_COOLDOWN = 30 * 60
MAX_RESTARTS = 2
RESTART_WINDOW = 6 * 60 * 60

YEELIGHT = {
    "b1": {
        "health": "binary_sensor.yeelight_b1_integration_healthy",
        "network": "binary_sensor.network_yeelight_b1_gateway",
        "entry_id": "01KPWMYB17HRAYT74F174724JV",
    },
    "1f": {
        "health": "binary_sensor.yeelight_1f_integration_healthy",
        "network": "binary_sensor.network_yeelight_1f_gateway",
        "entry_id": "01KPWMZ0127NWVYPM6HSKZ0S4A",
    },
    "2f": {
        "health": "binary_sensor.yeelight_2f_integration_healthy",
        "network": "binary_sensor.network_yeelight_2f_gateway",
        "entry_id": "01KQKB3CMGZ9QWPD4KQCTSZ2ME",
    },
    "3f": {
        "health": "binary_sensor.yeelight_3f_integration_healthy",
        "network": "binary_sensor.network_yeelight_3f_gateway",
        "entry_id": "01KQKAYF7Z6BZ2QGHQCD29NY20",
    },
}

HOMEKIT_PORTS = (21064, 21068)


def log(event: str, **data: object) -> None:
    print(json.dumps({"ts": int(time.time()), "event": event, **data}, ensure_ascii=False))


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"counters": {}, "last_actions": {}, "restart_history": []}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    os.chmod(tmp, 0o600)
    tmp.replace(STATE_FILE)


def token() -> str:
    return TOKEN_FILE.read_text().strip()


def api(path: str, payload: dict | None = None, timeout: float = 8.0):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        HA_URL + path,
        data=body,
        headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


def service(domain: str, name: str, payload: dict | None = None) -> None:
    api(f"/api/services/{domain}/{name}", payload or {}, timeout=15)


def notify(title: str, message: str) -> None:
    try:
        service(
            "persistent_notification",
            "create",
            {"title": title, "message": message, "notification_id": "ha_external_watchdog"},
        )
        service(
            "notify",
            "mobile_app_siqis_iphone",
            {"title": title, "message": message, "data": {"tag": "ha-external-watchdog"}},
        )
    except Exception as exc:  # HA may still be recovering.
        log("notify_failed", error=type(exc).__name__)


def tcp_open(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


def bump(state: dict, key: str, failed: bool) -> int:
    counters = state.setdefault("counters", {})
    counters[key] = counters.get(key, 0) + 1 if failed else 0
    return counters[key]


def cooldown_ready(state: dict, key: str, now: float) -> bool:
    return now - state.setdefault("last_actions", {}).get(key, 0) >= ACTION_COOLDOWN


def mark_action(state: dict, key: str, now: float) -> None:
    state.setdefault("last_actions", {})[key] = int(now)


def ssh(*args: str, timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", RASP_HOST, *args],
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def restart_allowed(state: dict, now: float) -> bool:
    history = [x for x in state.get("restart_history", []) if now - x < RESTART_WINDOW]
    state["restart_history"] = history
    return len(history) < MAX_RESTARTS and cooldown_ready(state, "ha_restart", now)


def recover_ha(state: dict, now: float, dry_run: bool) -> None:
    if not restart_allowed(state, now):
        log("ha_restart_suppressed", reason="cooldown_or_rate_limit")
        return
    check = ssh("docker", "exec", "homeassistant", "python", "-m", "homeassistant", "--script", "check_config", "-c", "/config")
    if check.returncode != 0:
        log("ha_restart_suppressed", reason="config_invalid", stderr=check.stderr[-300:])
        return
    log("ha_restart_planned", dry_run=dry_run)
    if dry_run:
        return
    result = ssh("docker", "restart", "homeassistant", timeout=120)
    if result.returncode == 0:
        mark_action(state, "ha_restart", now)
        state.setdefault("restart_history", []).append(int(now))
        state["counters"]["ha_api"] = 0
        log("ha_restarted")
    else:
        log("ha_restart_failed", stderr=result.stderr[-300:])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    now = time.time()
    state = load_state()

    try:
        start = time.monotonic()
        states_list = api("/api/states")
        latency = round(time.monotonic() - start, 3)
        states = {item["entity_id"]: item["state"] for item in states_list}
        api_failed = False
        log("ha_api_ok", latency_seconds=latency)
    except Exception as exc:
        states = {}
        api_failed = True
        log("ha_api_failed", error=type(exc).__name__)

    if bump(state, "ha_api", api_failed) >= FAILURE_THRESHOLD:
        recover_ha(state, now, args.dry_run)
        save_state(state)
        return 0

    if api_failed:
        save_state(state)
        return 0

    for floor, cfg in YEELIGHT.items():
        failed = states.get(cfg["network"]) == "on" and states.get(cfg["health"]) == "off"
        count = bump(state, f"yeelight_{floor}", failed)
        if count >= FAILURE_THRESHOLD and cooldown_ready(state, f"yeelight_{floor}", now):
            log("yeelight_reload_planned", floor=floor, dry_run=args.dry_run)
            if not args.dry_run:
                service("homeassistant", "reload_config_entry", {"entry_id": cfg["entry_id"]})
                mark_action(state, f"yeelight_{floor}", now)
                state["counters"][f"yeelight_{floor}"] = 0
                notify("易来集成自动恢复", f"{floor.upper()} 网关在线但实体不可用，已安全重载一次集成。")

    missing_ports = [port for port in HOMEKIT_PORTS if not tcp_open("192.168.3.254", port)]
    count = bump(state, "homekit", bool(missing_ports))
    if count >= FAILURE_THRESHOLD and cooldown_ready(state, "homekit", now):
        log("homekit_reload_planned", missing_ports=missing_ports, dry_run=args.dry_run)
        if not args.dry_run:
            service("homekit", "reload")
            mark_action(state, "homekit", now)
            state["counters"]["homekit"] = 0
            notify("HomeKit 桥接自动恢复", f"端口 {missing_ports} 连续不可用，已安全重载 HomeKit。")

    save_state(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
