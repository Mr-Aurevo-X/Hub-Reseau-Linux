# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal network diagnostics (ping/DNS placeholders)."""

from __future__ import annotations

import shutil
import socket
import subprocess


def quick_report() -> list[str]:
    lines: list[str] = []
    try:
        host = socket.gethostname()
        lines.append(f"Hostname: {host}")
    except OSError as exc:
        lines.append(f"Hostname: erreur ({exc})")
    if shutil.which("ping"):
        try:
            out = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "1.1.1.1"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            ok = out.returncode == 0
            lines.append(f"Ping 1.1.1.1: {'OK' if ok else 'échec'}")
        except (subprocess.SubprocessError, OSError) as exc:
            lines.append(f"Ping: {exc}")
    else:
        lines.append("Ping: commande indisponible")
    try:
        socket.getaddrinfo("github.com", 443)
        lines.append("DNS github.com: OK")
    except OSError as exc:
        lines.append(f"DNS github.com: {exc}")
    return lines
