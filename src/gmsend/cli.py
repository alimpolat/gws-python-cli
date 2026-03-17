"""gmsend CLI - Gmail from your terminal."""
import json as json_module
from pathlib import Path
from typing import Optional

import typer

from gmsend import __version__
from gmsend.output import (
    console,
    print_auth_status,
    print_error,
    print_inbox,
    print_info,
    print_json,
    print_message,
    print_sent,
    print_success,
    print_warning,
)

app = typer.Typer(
    name="gmsend",
    help="Gmail from your terminal. Attachments included.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    if value:
        console.print(f"gmsend {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    """Gmail from your terminal. Attachments included."""
    pass


@app.command()
def auth(
    status: bool = typer.Option(False, "--status", "-s", help="Show auth status."),
):
    """Authenticate with Gmail (opens browser for OAuth2)."""
    if status:
        from gmsend.auth import get_auth_status

        print_auth_status(get_auth_status())
        return

    from gmsend.auth import authenticate, has_client_secret

    if not has_client_secret():
        print_error(
            "No client_secret.json found.\n\n"
            "Setup:\n"
            "  1. Go to https://console.cloud.google.com/apis/credentials\n"
            "  2. Create an OAuth 2.0 Client ID (Desktop app)\n"
            "  3. Download the JSON and save it to:\n"
            "     ~/.config/gmsend/client_secret.json\n"
            "  4. Enable the Gmail API\n"
            "  5. Add your email as a test user\n"
        )
        raise typer.Exit(1)

    try:
        creds = authenticate()
        print_success("Authenticated successfully!")

        from gmsend.auth import get_auth_status
        print_auth_status(get_auth_status())

    except Exception as e:
        print_error(f"Authentication failed: {e}")
        raise typer.Exit(1)


@app.command()
def send(
    to: str = typer.Option(..., "--to", "-t", help="Recipient email(s), comma-separated."),
    subject: str = typer.Option(..., "--subject", "-s", help="Email subject."),
    body: str = typer.Option("", "--body", "-b", help="Email body text."),
    attach: Optional[list[str]] = typer.Option(
        None, "--attach", "-a", help="File to attach (repeatable)."
    ),
    cc: Optional[str] = typer.Option(None, "--cc", help="CC recipients, comma-separated."),
    bcc: Optional[str] = typer.Option(None, "--bcc", help="BCC recipients, comma-separated."),
    html: bool = typer.Option(False, "--html", help="Treat body as HTML."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without sending."),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """Send an email with optional attachments.

    Examples:
        gmsend send --to alice@example.com --subject "Hello" --body "Hi!"
        gmsend send --to bob@co.com --subject "Report" --attach report.pdf
        gmsend send --to team@co.com --subject "Files" --attach a.pdf --attach b.xlsx
    """
    # Validate attachments exist
    if attach:
        for filepath in attach:
            if not Path(filepath).exists():
                print_error(f"Attachment not found: {filepath}")
                raise typer.Exit(1)

    if dry_run:
        result = {
            "dry_run": True,
            "to": to,
            "subject": subject,
            "body_length": len(body),
            "attachments": [str(Path(f).name) for f in (attach or [])],
            "cc": cc,
            "bcc": bcc,
            "html": html,
        }
        if output_json:
            print_json(result)
        else:
            print_warning("[DRY RUN] Would send:")
            print_info(f"  To: {to}")
            print_info(f"  Subject: {subject}")
            if cc:
                print_info(f"  CC: {cc}")
            if attach:
                for f in attach:
                    print_info(f"  Attach: {Path(f).name}")
        return

    try:
        from gmsend.client import GmailClient

        client = GmailClient()
        result = client.send(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            attachments=attach,
            html=html,
        )

        if output_json:
            print_json(result)
        else:
            print_sent(
                message_id=result.get("id", "unknown"),
                to=to,
                subject=subject,
            )

    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Failed to send: {e}")
        raise typer.Exit(1)


@app.command()
def read(
    message_id: str = typer.Argument(..., help="Gmail message ID (from inbox listing)."),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """Read a full email message by ID.

    Examples:
        gmsend inbox                          # list messages, copy an ID
        gmsend read 19abc123def456            # read that message
        gmsend read 19abc123def456 --json     # raw JSON output
    """
    try:
        from gmsend.client import GmailClient

        client = GmailClient()
        msg = client.read(message_id)

        if output_json:
            print_json(msg)
        else:
            print_message(msg)

    except Exception as e:
        print_error(f"Failed to read message: {e}")
        raise typer.Exit(1)


@app.command()
def inbox(
    max_results: int = typer.Option(10, "--max", "-n", help="Number of messages to show."),
    query: str = typer.Option("", "--query", "-q", help="Gmail search query."),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """List inbox messages."""
    try:
        from gmsend.client import GmailClient

        client = GmailClient()
        messages = client.inbox(max_results=max_results, query=query)

        if output_json:
            print_json(messages)
        else:
            print_inbox(messages)

    except Exception as e:
        print_error(f"Failed to read inbox: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
