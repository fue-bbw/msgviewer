import json
from pathlib import Path

from msgviewer import MessageSummary
from msgviewer.viewer import format_json, format_text, main


def test_format_text(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    text = format_text(summary)
    assert "Betreff : Test E-Mail" in text
    assert "elias.laugher@gmail.com" in text
    assert "Anhänge : 0" in text
    assert "Just a test to get an email with one cc recipient." in text


def test_format_text_no_body(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    text = format_text(summary, show_body=False)
    assert "Just a test" not in text


def test_format_text_attachments(attachments_msg: Path):
    summary = MessageSummary.from_file(attachments_msg)
    text = format_text(summary)
    assert "Anhänge : 2" in text
    assert ".bin" in text


def test_format_json(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    payload = json.loads(format_json(summary))
    assert payload["subject"] == "Test E-Mail"
    assert payload["date"].startswith("2020-01-07")
    assert payload["attachments"] == []


def test_main_json(simple_msg: Path, capsys):
    assert main([str(simple_msg), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["subject"] == "Test E-Mail"


def test_main_missing_file(tmp_path: Path, capsys):
    assert main([str(tmp_path / "fehlt.msg")]) == 2
    assert "Fehler" in capsys.readouterr().err
