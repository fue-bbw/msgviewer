from datetime import datetime
from pathlib import Path

import pytest

from msgviewer import MessageSummary


def test_from_file_simple(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    assert summary.subject == "Test E-Mail"
    assert "elias.laugher@gmail.com" in summary.sender
    assert "Sven Sielenkemper" in summary.to
    assert "niklas.lindson@gmail.com" in summary.cc
    assert isinstance(summary.date, datetime)
    assert summary.date.year == 2020
    assert "Just a test to get an email with one cc recipient." in summary.body
    assert summary.html_body is not None
    assert "Just a test" in summary.html_body
    assert summary.attachments == []


def test_from_file_attachments(attachments_msg: Path):
    summary = MessageSummary.from_file(attachments_msg)
    assert "Bosco Fraud Cases" in summary.subject
    assert len(summary.attachments) == 2
    for att in summary.attachments:
        assert att.filename
        assert att.size > 0
        assert "/" in att.mimetype
        assert att.data


def test_from_file_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        MessageSummary.from_file(tmp_path / "nicht-da.msg")
