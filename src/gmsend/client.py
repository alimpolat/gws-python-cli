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
