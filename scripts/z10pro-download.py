#!/usr/bin/env python3
"""Control the private aria2 download service running on the Z10 Pro."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


RPC_URL = os.environ.get(
    "Z10PRO_ARIA2_URL", "http://192.168.3.115:6800/jsonrpc"
)
SECRET_FILE = Path(
    os.environ.get(
        "Z10PRO_ARIA2_SECRET_FILE",
        "~/.config/z10pro/aria2-rpc.secret",
    )
).expanduser()


def rpc(method: str, params: list[object] | None = None) -> object:
    try:
        secret = SECRET_FILE.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise SystemExit(f"Cannot read RPC secret {SECRET_FILE}: {exc}") from exc

    payload = {
        "jsonrpc": "2.0",
        "id": "rasp2",
        "method": f"aria2.{method}",
        "params": [f"token:{secret}", *(params or [])],
    }
    request = urllib.request.Request(
        RPC_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.load(response)
    except (OSError, urllib.error.URLError) as exc:
        raise SystemExit(f"Cannot reach {RPC_URL}: {exc}") from exc

    if "error" in result:
        raise SystemExit(f"aria2 RPC error: {result['error']}")
    return result.get("result")


def human_size(value: str | int) -> str:
    size = float(value or 0)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TiB"


def task_name(task: dict[str, object]) -> str:
    files = task.get("files") or []
    if files and isinstance(files, list):
        path = str(files[0].get("path", ""))
        if path:
            return Path(path).name
    return str(task.get("bittorrent", {}).get("info", {}).get("name", "-"))


def print_tasks(tasks: list[dict[str, object]]) -> None:
    if not tasks:
        print("No download tasks.")
        return
    print(f"{'GID':16} {'STATUS':9} {'PROGRESS':>9} {'SPEED':>10} NAME")
    for task in tasks:
        total = int(task.get("totalLength", 0) or 0)
        done = int(task.get("completedLength", 0) or 0)
        progress = f"{done * 100 / total:.1f}%" if total else "-"
        speed = f"{human_size(task.get('downloadSpeed', 0))}/s"
        print(
            f"{str(task.get('gid', '-'))[:16]:16} "
            f"{str(task.get('status', '-')):9} {progress:>9} {speed:>10} "
            f"{task_name(task)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an HTTP(S), FTP, magnet, or torrent URL")
    add.add_argument("url")
    add.add_argument("--out", help="output filename for a single-file download")

    sub.add_parser("list", help="list active, waiting, and recent tasks")
    status = sub.add_parser("status", help="show one task as JSON")
    status.add_argument("gid")
    for name in ("pause", "resume", "remove"):
        action = sub.add_parser(name)
        action.add_argument("gid")
    sub.add_parser("purge", help="clear completed/error task records")
    sub.add_parser("version", help="show aria2 version")

    args = parser.parse_args()
    if args.command == "add":
        options = {"out": args.out} if args.out else {}
        print(rpc("addUri", [[args.url], options]))
    elif args.command == "list":
        fields = [
            "gid",
            "status",
            "totalLength",
            "completedLength",
            "downloadSpeed",
            "files",
            "bittorrent",
        ]
        tasks: list[dict[str, object]] = []
        tasks.extend(rpc("tellActive", [fields]))
        tasks.extend(rpc("tellWaiting", [0, 100, fields]))
        tasks.extend(rpc("tellStopped", [0, 20, fields]))
        print_tasks(tasks)
    elif args.command == "status":
        print(json.dumps(rpc("tellStatus", [args.gid]), ensure_ascii=False, indent=2))
    elif args.command == "pause":
        print(rpc("pause", [args.gid]))
    elif args.command == "resume":
        print(rpc("unpause", [args.gid]))
    elif args.command == "remove":
        try:
            print(rpc("remove", [args.gid]))
        except SystemExit:
            print(rpc("removeDownloadResult", [args.gid]))
    elif args.command == "purge":
        print(rpc("purgeDownloadResult"))
    elif args.command == "version":
        print(json.dumps(rpc("getVersion"), indent=2))


if __name__ == "__main__":
    main()
