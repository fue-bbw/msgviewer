from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from .message import MessageSummary


def format_text(summary: MessageSummary, show_body: bool = True) -> str:
    lines = [
        f"Betreff : {summary.subject}",
        f"Von     : {summary.sender}",
        f"An      : {summary.to}",
    ]
    if summary.cc:
        lines.append(f"Cc      : {summary.cc}")
    if summary.date:
        lines.append(f"Datum   : {summary.date}")
    lines.append(f"Anhänge : {len(summary.attachments)}")
    for att in summary.attachments:
        lines.append(f"  - {att.filename} ({att.size} Bytes, {att.mimetype})")
    if show_body:
        lines.append("")
        lines.append("--- Nachrichtentext ---")
        lines.append(summary.body.rstrip())
    return "\n".join(lines)


def format_json(summary: MessageSummary) -> str:
    payload = {
        "subject": summary.subject,
        "sender": summary.sender,
        "to": summary.to,
        "cc": summary.cc,
        "date": summary.date.isoformat() if summary.date else None,
        "body": summary.body,
        "html_body": summary.html_body,
        "attachments": [
            {"filename": a.filename, "size": a.size, "mimetype": a.mimetype}
            for a in summary.attachments
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="msgviewer",
        description="Zeigt den Inhalt einer Outlook-.msg-Datei an.",
    )
    parser.add_argument("msg", type=Path, help="Pfad zur .msg-Datei")
    parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    parser.add_argument("--no-body", action="store_true", help="Nachrichtentext nicht ausgeben")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = MessageSummary.from_file(args.msg)
    except FileNotFoundError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(format_json(summary))
    else:
        print(format_text(summary, show_body=not args.no_body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
