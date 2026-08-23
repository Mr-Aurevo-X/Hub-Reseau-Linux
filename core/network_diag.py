# SPDX-License-Identifier: GPL-3.0-or-later
"""Extended network diagnostics."""

from __future__ import annotations

import socket
import time
from pathlib import Path

from core import host, i18n


def quick_report(host_name: str = "1.1.1.1") -> list[str]:
    lines: list[str] = []
    try:
        lines.append(i18n.t("diag_hostname", name=socket.gethostname()))
    except OSError as exc:
        lines.append(i18n.t("diag_hostname", name=str(exc)))

    target = (host_name or "1.1.1.1").strip() or "1.1.1.1"
    if host.which("ping"):
        try:
            out = host.run(
                ["ping", "-c", "1", "-W", "2", target],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            key = "diag_ping_ok" if out.returncode == 0 else "diag_ping_fail"
            lines.append(i18n.t(key, target=target))
        except (OSError, TimeoutError) as exc:
            lines.append(i18n.t("diag_ping_error", detail=str(exc)))
    else:
        lines.append(i18n.t("diag_ping_missing"))

    for domain in ("github.com", "flathub.org"):
        try:
            socket.getaddrinfo(domain, 443)
            lines.append(i18n.t("diag_dns_ok", domain=domain))
        except OSError as exc:
            lines.append(i18n.t("diag_dns_fail", domain=domain, detail=str(exc)))

    lines.extend(_listening_ports())
    lines.extend(traceroute_lines(target))
    return lines


def traceroute_lines(host_name: str) -> list[str]:
    target = (host_name or "1.1.1.1").strip() or "1.1.1.1"
    missing = [i18n.t("diag_trace_missing")]
    if host.which("mtr"):
        cmd = ["mtr", "-n", "-r", "-c", "1", "--", target]
    elif host.which("traceroute"):
        cmd = ["traceroute", "-n", "-w", "2", "-m", "12", "--", target]
    else:
        return missing
    try:
        out = host.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, TimeoutError):
        return missing
    text = (out.stdout or out.stderr or "").strip()
    if not text:
        return missing
    return text.splitlines()


def export_report(host_name: str) -> str:
    return "\n".join(quick_report(host_name))


def default_export_path() -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return Path.home() / "Documents" / f"hub-reseau-diag-{stamp}.txt"


def write_export(host_name: str, path: Path | None = None, *, text: str | None = None) -> Path:
    target = path or default_export_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text if text is not None else export_report(host_name), encoding="utf-8")
    return target


def _listening_ports() -> list[str]:
    if not host.which("ss"):
        return []
    try:
        out = host.run(
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
            return [i18n.t("diag_ports_header")] + rows
    except (OSError, TimeoutError):
        pass
    return []
