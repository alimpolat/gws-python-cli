"""Tests for MIME message building."""
import base64
import email
import os
import tempfile
from pathlib import Path

from gmsend.mime import build_message, get_attachment_info


def test_simple_message():
    """Test building a plain text message without attachments."""
    result = build_message(
        to="alice@example.com",
        subject="Hello",
        body="Hi Alice!",
    )
    assert "raw" in result
    raw = base64.urlsafe_b64decode(result["raw"])
    msg = email.message_from_bytes(raw)
    assert msg["To"] == "alice@example.com"
    assert msg["Subject"] == "Hello"
    assert "Hi Alice!" in msg.get_payload(decode=True).decode()


def test_message_with_cc_bcc():
    """Test CC and BCC headers."""
    result = build_message(
        to="alice@example.com",
        subject="Test",
        body="Body",
        cc="bob@example.com",
        bcc="charlie@example.com",
    )
    raw = base64.urlsafe_b64decode(result["raw"])
    msg = email.message_from_bytes(raw)
    assert msg["Cc"] == "bob@example.com"
    assert msg["Bcc"] == "charlie@example.com"


def test_html_message():
    """Test HTML body."""
    result = build_message(
        to="alice@example.com",
        subject="HTML",
        body="<h1>Hello</h1>",
        html=True,
    )
    raw = base64.urlsafe_b64decode(result["raw"])
    msg = email.message_from_bytes(raw)
    assert msg.get_content_type() == "text/html"


def test_message_with_attachment():
    """Test attaching a file."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("test content")
        tmpfile = f.name

    try:
        result = build_message(
            to="alice@example.com",
            subject="With attachment",
            body="See attached.",
            attachments=[tmpfile],
        )
        raw = base64.urlsafe_b64decode(result["raw"])
        msg = email.message_from_bytes(raw)

        assert msg.get_content_type() == "multipart/mixed"
        parts = msg.get_payload()
        assert len(parts) == 2  # body + 1 attachment
        assert parts[1].get_filename() == Path(tmpfile).name
    finally:
        os.unlink(tmpfile)


def test_message_with_multiple_attachments():
    """Test multiple attachments."""
    files = []
    try:
        for ext in [".pdf", ".xlsx", ".png"]:
            f = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            f.write(b"fake content")
            f.close()
            files.append(f.name)

        result = build_message(
            to="alice@example.com",
            subject="Multiple",
            body="Files attached.",
            attachments=files,
        )
        raw = base64.urlsafe_b64decode(result["raw"])
        msg = email.message_from_bytes(raw)

        parts = msg.get_payload()
        assert len(parts) == 4  # body + 3 attachments
    finally:
        for f in files:
            os.unlink(f)


def test_missing_attachment_raises():
    """Test that missing file raises FileNotFoundError."""
    import pytest

    with pytest.raises(FileNotFoundError):
        build_message(
            to="alice@example.com",
            subject="Test",
            body="Body",
            attachments=["/nonexistent/file.pdf"],
        )


def test_attachment_info():
    """Test get_attachment_info."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"x" * 1024)
        tmpfile = f.name

    try:
        info = get_attachment_info(tmpfile)
        assert info["filename"].endswith(".pdf")
        assert info["size_bytes"] == 1024
        assert info["mime_type"] == "application/pdf"
        assert info["exists"] is True
    finally:
        os.unlink(tmpfile)
