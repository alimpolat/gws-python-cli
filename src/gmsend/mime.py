"""MIME message builder with attachment support."""
import base64
import mimetypes
import os
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path


def build_message(
    to: str,
    subject: str,
    body: str,
    cc: str | None = None,
    bcc: str | None = None,
    attachments: list[str] | None = None,
    html: bool = False,
) -> dict:
    """Build a Gmail API message with optional attachments.

    Args:
        to: Recipient email(s), comma-separated.
        subject: Email subject line.
        body: Email body (plain text or HTML).
        cc: CC recipients, comma-separated.
        bcc: BCC recipients, comma-separated.
        attachments: List of file paths to attach.
        html: If True, treat body as HTML.

    Returns:
        dict with 'raw' key containing base64url-encoded message.
    """
    if attachments:
        msg = MIMEMultipart()
        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        for filepath in attachments:
            _attach_file(msg, filepath)
    else:
        content_type = "html" if html else "plain"
        msg = MIMEText(body, content_type, "utf-8")

    msg["To"] = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def _attach_file(msg: MIMEMultipart, filepath: str) -> None:
    """Attach a file to a MIME message, auto-detecting the MIME type."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Attachment not found: {filepath}")

    content_type, _ = mimetypes.guess_type(str(path))
    if content_type is None:
        content_type = "application/octet-stream"

    main_type, sub_type = content_type.split("/", 1)
    filename = path.name

    with open(path, "rb") as f:
        file_data = f.read()

    if main_type == "text":
        part = MIMEText(file_data.decode("utf-8", errors="replace"), _subtype=sub_type)
    elif main_type == "image":
        part = MIMEImage(file_data, _subtype=sub_type)
    elif main_type == "audio":
        part = MIMEAudio(file_data, _subtype=sub_type)
    else:
        part = MIMEBase(main_type, sub_type)
        part.set_payload(file_data)
        encoders.encode_base64(part)

    part.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(part)


def get_attachment_info(filepath: str) -> dict:
    """Get info about a file to be attached."""
    path = Path(filepath)
    content_type, _ = mimetypes.guess_type(str(path))
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "mime_type": content_type or "application/octet-stream",
        "exists": path.exists(),
    }
