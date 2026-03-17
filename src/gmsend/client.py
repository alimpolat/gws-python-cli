"""Gmail client - core send/read logic."""
from gmsend.auth import get_gmail_service
from gmsend.mime import build_message


class GmailClient:
    """High-level Gmail client wrapping the Gmail API."""

    def __init__(self, service=None):
        self._service = service

    @property
    def service(self):
        if self._service is None:
            self._service = get_gmail_service()
        return self._service

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str | None = None,
        bcc: str | None = None,
        attachments: list[str] | None = None,
        html: bool = False,
    ) -> dict:
        """Send an email with optional attachments.

        Args:
            to: Recipient email(s), comma-separated.
            subject: Email subject.
            body: Email body text (or HTML if html=True).
            cc: CC recipients.
            bcc: BCC recipients.
            attachments: List of file paths to attach.
            html: Treat body as HTML.

        Returns:
            Gmail API response dict with 'id', 'threadId', 'labelIds'.
        """
        message = build_message(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            html=html,
        )
        return self.service.users().messages().send(userId="me", body=message).execute()

    def read(self, message_id: str) -> dict:
        """Read a full email message by ID.

        Args:
            message_id: Gmail message ID (from inbox listing).

        Returns:
            Dict with id, threadId, from, to, cc, subject, date, body, attachments.
        """
        full = self.service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        body = self._extract_body(full["payload"])
        attachment_names = self._extract_attachment_names(full["payload"])

        return {
            "id": full["id"],
            "threadId": full.get("threadId", ""),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "cc": headers.get("Cc", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body,
            "snippet": full.get("snippet", ""),
            "attachments": attachment_names,
        }

    def _extract_body(self, payload: dict) -> str:
        """Extract plain text body from a Gmail message payload."""
        import base64

        # Simple single-part message
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

        # Multipart — look for text/plain first, then text/html
        parts = payload.get("parts", [])
        plain = ""
        html = ""
        for part in parts:
            mime = part.get("mimeType", "")
            data = part.get("body", {}).get("data", "")
            if mime == "text/plain" and data:
                plain = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            elif mime == "text/html" and data:
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            # Recurse into nested multipart
            if part.get("parts"):
                nested = self._extract_body(part)
                if nested and not plain:
                    plain = nested

        return plain or html

    def _extract_attachment_names(self, payload: dict) -> list[str]:
        """Extract attachment filenames from a Gmail message payload."""
        names = []
        for part in payload.get("parts", []):
            filename = part.get("filename", "")
            if filename:
                names.append(filename)
            if part.get("parts"):
                names.extend(self._extract_attachment_names(part))
        return names

    def inbox(self, max_results: int = 10, query: str = "") -> list[dict]:
        """List inbox messages.

        Args:
            max_results: Maximum number of messages to return.
            query: Gmail search query (e.g., 'from:alice@example.com').

        Returns:
            List of message dicts with id, subject, from, date, snippet.
        """
        params = {"userId": "me", "maxResults": max_results, "labelIds": ["INBOX"]}
        if query:
            params["q"] = query

        results = self.service.users().messages().list(**params).execute()
        messages = results.get("messages", [])

        detailed = []
        for msg in messages:
            full = self.service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
            detailed.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": full.get("snippet", ""),
            })

        return detailed
