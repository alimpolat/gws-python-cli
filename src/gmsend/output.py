"""Rich console output helpers."""
import json as json_module

from rich.console import Console
from rich.table import Table

console = Console()
error_console = Console(stderr=True)


def print_success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def print_error(message: str) -> None:
    error_console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


def print_info(message: str) -> None:
    console.print(f"[dim]{message}[/dim]")


def print_sent(message_id: str, to: str, subject: str) -> None:
    console.print(f"[green]Sent![/green] Message ID: {message_id}")
    console.print(f"  To: {to}")
    console.print(f"  Subject: {subject}")


def print_json(data: dict) -> None:
    console.print_json(json_module.dumps(data, indent=2, default=str))


def print_auth_status(status: dict) -> None:
    table = Table(title="gmsend Auth Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Config dir", status["config_dir"])
    table.add_row(
        "Client secret",
        "[green]Found[/green]" if status["client_secret"] else "[red]Missing[/red]",
    )
    table.add_row(
        "Token",
        "[green]Found[/green]" if status["token"] else "[red]Missing[/red]",
    )
    table.add_row(
        "Authenticated",
        "[green]Yes[/green]" if status["authenticated"] else "[red]No[/red]",
    )
    if status.get("email"):
        table.add_row("Email", f"[bold]{status['email']}[/bold]")

    console.print(table)


def print_inbox(messages: list[dict]) -> None:
    table = Table(title="Inbox")
    table.add_column("Date", style="dim", width=24)
    table.add_column("From", style="cyan", width=30)
    table.add_column("Subject", width=50)

    for msg in messages:
        table.add_row(msg["date"][:24], msg["from"][:30], msg["subject"][:50])

    console.print(table)
