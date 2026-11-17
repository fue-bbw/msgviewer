import email
from email import policy
from pathlib import Path

from msgviewer import MessageSummary
from msgviewer.converter import convert, main, save_attachments, to_eml, to_html, to_txt


def test_to_txt(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    text = to_txt(summary)
    assert "Betreff: Test E-Mail" in text
    assert "Von: " in text and "elias.laugher@gmail.com" in text
    assert "Just a test to get an email with one cc recipient." in text


def test_to_html_prefers_html_body(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    doc = to_html(summary)
    assert '<div dir="auto">' in doc


def test_to_html_fallback_escapes_text():
    from msgviewer.message import AttachmentInfo, MessageSummary as MS

    summary = MS(subject="<b>", sender="a@b.c", to="d@e.f", cc="", date=None,
                 body="<script>alert(1)</script>", html_body=None, attachments=[])
    doc = to_html(summary)
    assert "<script>" not in doc
    assert "&lt;script&gt;" in doc


def test_to_eml_headers_and_body(simple_msg: Path):
    summary = MessageSummary.from_file(simple_msg)
    raw = to_eml(summary)
    msg = email.message_from_bytes(raw, policy=policy.default)
    assert msg["Subject"] == "Test E-Mail"
    assert "elias.laugher@gmail.com" in msg["From"]
    assert "niklas.lindson@gmail.com" in msg["Cc"]
    assert msg["Date"] is not None
    assert "Just a test to get an email with one cc recipient." in msg.get_body(preferencelist=("plain",)).get_content()
    assert msg.get_body(preferencelist=("html",)) is not None


def test_to_eml_attachments(attachments_msg: Path):
    summary = MessageSummary.from_file(attachments_msg)
    msg = email.message_from_bytes(to_eml(summary), policy=policy.default)
    attachments = list(msg.iter_attachments())
    assert len(attachments) == 2
    for att in attachments:
        assert att.get_filename().endswith(".bin")
        assert len(att.get_payload(decode=True)) > 0


def test_convert_unknown_format(simple_msg: Path):
    import pytest

    summary = MessageSummary.from_file(simple_msg)
    with pytest.raises(ValueError):
        convert(summary, "pdf")


def test_save_attachments(attachments_msg: Path, tmp_path: Path):
    summary = MessageSummary.from_file(attachments_msg)
    written = save_attachments(summary, tmp_path / "anhaenge")
    assert len(written) == 2
    for att, path in zip(summary.attachments, written):
        assert path.name == att.filename
        assert path.read_bytes() == att.data


def test_main_writes_eml(simple_msg: Path, tmp_path: Path, capsys):
    out = tmp_path / "out.eml"
    assert main([str(simple_msg), "-f", "eml", "-o", str(out)]) == 0
    assert out.is_file()
    msg = email.message_from_bytes(out.read_bytes(), policy=policy.default)
    assert msg["Subject"] == "Test E-Mail"
    assert "out.eml" in capsys.readouterr().out


def test_main_default_output_name(simple_msg: Path, capsys):
    assert main([str(simple_msg), "-f", "txt"]) == 0
    expected = simple_msg.with_suffix(".txt")
    assert expected.is_file()
    assert expected.read_text(encoding="utf-8").startswith("Betreff: Test E-Mail")
    expected.unlink()


def test_main_attachments_dir(attachments_msg: Path, tmp_path: Path):
    out = tmp_path / "out.txt"
    att_dir = tmp_path / "att"
    assert main([str(attachments_msg), "-f", "txt", "-o", str(out), "--attachments", str(att_dir)]) == 0
    assert len(list(att_dir.iterdir())) == 2


def test_main_missing_file(tmp_path: Path, capsys):
    assert main([str(tmp_path / "fehlt.msg")]) == 2
    assert "Fehler" in capsys.readouterr().err
