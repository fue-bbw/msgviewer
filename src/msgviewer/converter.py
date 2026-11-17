from __future__ import annotations

import argparse
import html
import sys
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path
from typing import Optional, Sequence, Union

from .message import MessageSummary

FORMATS = ("eml", "html", "txt")


def to_txt(summary: MessageSummary) -> str:
    lines = [
        f"Betreff: {summary.subject}",
        f"Von: {summary.sender}",
        f"An: {summary.to}",
    ]
    if summary.cc:
        lines.append(f"Cc: {summary.cc}")
    if summary.date:
        lines.append(f"Datum: {summary.date}")
    lines.append("")
    lines.append(summary.body.rstrip())
    return "\n".join(lines) + "\n"


def to_html(summary: MessageSummary) -> str:
    if summary.html_body:
        return summary.html_body
    body = html.escape(summary.body)
    return (
        "<!DOCTYPE html>\n<html>\n<head><meta charset=\"utf-8\">"
        f"<title>{html.escape(summary.subject)}</title></head>\n"
        f"<body><pre>{body}</pre></body>\n</html>\n"
    )


def to_eml(summary: MessageSummary) -> bytes:
    msg = EmailMessage()
    msg["Subject"] = summary.subject
    msg["From"] = summary.sender
    msg["To"] = summary.to
    if summary.cc:
        msg["Cc"] = summary.cc
    if isinstance(summary.date, datetime):
        msg["Date"] = format_datetime(summary.date)
    elif summary.date:
        msg["Date"] = str(summary.date)
    if summary.html_body:
        msg.set_content(summary.body)
        msg.add_alternative(summary.html_body, subtype="html")
    else:
        msg.set_content(summary.body)
    for att in summary.attachments:
        maintype, _, subtype = att.mimetype.partition("/")
        if not subtype or maintype == "message":
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(att.data, maintype=maintype, subtype=subtype, filename=att.filename)
    return msg.as_bytes()


def convert(summary: MessageSummary, fmt: str) -> Union[bytes, str]:
    if fmt == "eml":
        return to_eml(summary)
    if fmt == "html":
        return to_html(summary)
    if fmt == "txt":
        return to_txt(summary)
    raise ValueError(f"Unbekanntes Format: {fmt} (erlaubt: {', '.join(FORMATS)})")


def save_attachments(summary: MessageSummary, directory: Union[str, Path]) -> list[Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for att in summary.attachments:
        target = directory / Path(att.filename).name
        target.write_bytes(att.data)
        written.append(target)
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="msgconvert",
        description="Wandelt eine Outlook-.msg-Datei in ein anderes Format um.",
    )
    parser.add_argument("msg", type=Path, help="Pfad zur .msg-Datei")
    parser.add_argument("-f", "--format", choices=FORMATS, default="eml", help="Zielformat (Standard: eml)")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Zieldatei (Standard: <name>.<format>)")
    parser.add_argument("--attachments", type=Path, default=None, help="Verzeichnis zum Speichern der Anhänge")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = MessageSummary.from_file(args.msg)
    except FileNotFoundError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2
    output = args.output or args.msg.with_suffix(f".{args.format}")
    result = convert(summary, args.format)
    if isinstance(result, bytes):
        output.write_bytes(result)
    else:
        output.write_text(result, encoding="utf-8")
    print(f"Geschrieben: {output}")
    if args.attachments:
        written = save_attachments(summary, args.attachments)
        for path in written:
            print(f"Anhang gespeichert: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
