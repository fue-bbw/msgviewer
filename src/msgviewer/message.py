from __future__ import annotations

import mimetypes
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import extract_msg


@dataclass
class AttachmentInfo:
    filename: str
    data: bytes
    mimetype: str

    @property
    def size(self) -> int:
        return len(self.data)


@dataclass
class MessageSummary:
    subject: str
    sender: str
    to: str
    cc: str
    date: Optional[Union[datetime, str]]
    body: str
    html_body: Optional[str]
    attachments: list[AttachmentInfo] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> MessageSummary:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Datei nicht gefunden: {path}")
        msg = extract_msg.openMsg(str(path))
        try:
            attachments = [
                AttachmentInfo(
                    filename=_attachment_filename(att),
                    data=att.data,
                    mimetype=att.mimetype or _guess_mimetype(_attachment_filename(att)),
                )
                for att in msg.attachments
            ]
            html_body = None
            if msg.htmlBody:
                html_body = msg.htmlBody.decode("utf-8", errors="replace")
            return cls(
                subject=msg.subject or "",
                sender=msg.sender or "",
                to=msg.to or "",
                cc=msg.cc or "",
                date=msg.date,
                body=msg.body or "",
                html_body=html_body,
                attachments=attachments,
            )
        finally:
            msg.close()


def _attachment_filename(att) -> str:
    for attr in ("longFilename", "shortFilename", "displayName"):
        value = getattr(att, attr, None)
        if value:
            return value
    try:
        return att.getFilename()
    except Exception:
        return "attachment.bin"


def _guess_mimetype(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"
