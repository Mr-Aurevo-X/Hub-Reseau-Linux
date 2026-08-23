# SPDX-License-Identifier: GPL-3.0-or-later
"""Extended network diagnostics."""

from __future__ import annotations

import re
import shutil
import socket
import subprocess
from typing import Any


def quick_report(host: str = "1.1.1.1") -> list[str]:
    lines: list[str] = []
    try:
        lines.append(f"Hostname: {socket.gethostname()}")
    except OSError as exc:
        lines.append(f"Hostname: {exc}")

    target = (host or "1.1.1.1").strip() or "1.1.1.1"
    if shutil.which("ping"):
        try:
            out = subprocess.run(
                ["ping", "-c", "1", "-W", "2", target],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            lines.append(f"Ping {target}: {'OK' if out.returncode == 0 else 'échec'}")
        except (subprocess.SubprocessError, OSError) as exc:
            lines.append(f"Ping: {exc}")
    else:
        lines.append("Ping: commande indisponible")

    for domain in ("github.com", "flathub.org"):
        try:
            socket.getaddrinfo(domain, 443)
            lines.append(f"DNS {domain}: OK")
        except OSError as exc:
            lines.append(f"DNS {domain}: {exc}")

    lines.extend(_listening_ports())
    lines.extend(traceroute_lines(target))
    return lines


def traceroute_lines(host: str) -> list[str]:
    target = (host or "1.1.1.1").strip() or "1.1.1.1"
    if shutil.which("mtr"):
        cmd = ["mtr", "-n", "-r", "-c", "1", "--", target]
    elif shutil.which("traceroute"):
        cmd = ["traceroute", "-n", "-w", "2", "-m", "12", "--", target]
    else:
        return ["traceroute/mtr indisponible"]
    try:
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (subprocess.SubprocessError, OSError):
        return ["traceroute/mtr indisponible"]
    text = (out.stdout or out.stderr or "").strip()
    if not text:
        return ["traceroute/mtr indisponible"]
    return text.splitlines()


def export_report(host: str) -> str:
    return "\n".join(quick_report(host))


def _listening_ports() -> list[str]:
    if shutil.which("ss"):
        try:
            out = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=4,
                check=False,
            )
            rows = []
            for line in (out.stdout or "").splitlines()[1:]:
                if "127.0.0.1:" in line or "0.0.0.0:" in line or "[::]:" in line:
                    rows.append(line.strip())
                if len(rows) >= 8:
                    break
            if rows:
                return ["Ports en écoute (extrait):"] + rows
        except (subprocess.SubprocessError, OSError):
            pass
    return []
