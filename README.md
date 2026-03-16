<h1 align="center">gmsend</h1>

<p align="center"><strong>Gmail from your terminal. Attachments included.</strong></p>

<p align="center">
  <a href="https://pypi.org/project/gmsend/"><img src="https://img.shields.io/pypi/v/gmsend" alt="PyPI version"></a>
  <a href="https://pypi.org/project/gmsend/"><img src="https://img.shields.io/pypi/pyversions/gmsend" alt="Python versions"></a>
  <a href="https://github.com/alimpolat/gmsend/blob/main/LICENSE"><img src="https://img.shields.io/github/license/alimpolat/gmsend" alt="License"></a>
  <a href="https://github.com/alimpolat/gmsend/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/alimpolat/gmsend/ci.yml?branch=main&label=CI" alt="CI"></a>
</p>

---

## The Problem

Google's official [Workspace CLI](https://github.com/googleworkspace/cli) (`gws`) can send emails via Gmail — but **cannot attach files** ([issue #498](https://github.com/googleworkspace/cli/issues/498)). [yagmail](https://github.com/kootenpv/yagmail) uses SMTP (requires app passwords, breaks with 2FA). [simplegmail](https://github.com/jeremyephron/simplegmail) is a library, not a CLI.

## The Solution

```bash
pip install gmsend
gmsend auth                    # One-time OAuth2 setup (browser opens)
gmsend send \
  --to alice@example.com \
  --subject "Q1 Report" \
  --body "Please find the report attached." \
  --attach report.pdf
```

That's it. Three commands. No SMTP. No app passwords. Just Gmail API + OAuth2.

## Features

- **Send with attachments** — any file type, multiple files
- **OAuth2** — no SMTP passwords, no app passwords, works with 2FA
- **CLI interface** — `pip install` and go
- **Read inbox** — `gmsend inbox` to check your email
- **Rich output** — colored terminal output with tables
- **JSON mode** — `--json` flag for scripting and piping
- **Dry run** — `--dry-run` to preview without sending
- **Cross-platform** — Windows, macOS, Linux
- **Python library** — `from gmsend.client import GmailClient` for programmatic use

## Quick Start

### 1. Install

```bash
pip install gmsend
```

### 2. Set up Google OAuth (one-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a project (or use an existing one)
3. Enable the [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
4. Configure the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) (External, add your email as test user)
5. Create an **OAuth 2.0 Client ID** (Desktop app)
6. Download the JSON and save it to `~/.config/gmsend/client_secret.json`

### 3. Authenticate

```bash
gmsend auth
```

A browser window opens. Sign in, grant permissions. Done. Token is saved — you won't need to do this again.

### 4. Send

```bash
gmsend send --to boss@company.com --subject "Report" --body "Attached." --attach report.pdf
```

## Usage Examples

### Send a simple email

```bash
gmsend send --to alice@example.com --subject "Hello" --body "Hi Alice!"
```

### Send with attachment

```bash
gmsend send \
  --to alice@example.com \
  --subject "Invoice" \
  --body "Please find the invoice attached." \
  --attach invoice.pdf
```

### Multiple attachments

```bash
gmsend send \
  --to team@company.com \
  --subject "Project Files" \
  --body "All files attached." \
  --attach report.pdf \
  --attach data.xlsx \
  --attach screenshot.png
```

### CC and BCC

```bash
gmsend send \
  --to alice@example.com \
  --subject "Update" \
  --body "FYI" \
  --cc bob@example.com \
  --bcc manager@example.com
```

### HTML body

```bash
gmsend send \
  --to alice@example.com \
  --subject "Newsletter" \
  --body "<h1>Hello!</h1><p>Welcome to our newsletter.</p>" \
  --html
```

### Dry run (preview without sending)

```bash
gmsend send --to alice@example.com --subject "Test" --body "Hi" --attach file.pdf --dry-run
```

### JSON output (for scripting)

```bash
gmsend send --to alice@example.com --subject "Test" --body "Hi" --json
```

### Check inbox

```bash
gmsend inbox
gmsend inbox --max 20
gmsend inbox --query "from:alice@example.com"
```

### Check auth status

```bash
gmsend auth --status
```

## Python Library

```python
from gmsend.client import GmailClient

client = GmailClient()

# Send with attachment
client.send(
    to="alice@example.com",
    subject="Report",
    body="See attached.",
    attachments=["report.pdf", "data.xlsx"],
)

# Read inbox
messages = client.inbox(max_results=5)
for msg in messages:
    print(f"{msg['from']}: {msg['subject']}")
```

## vs. Alternatives

| Feature | **gmsend** | gws CLI | yagmail | simplegmail |
|---------|-----------|---------|---------|-------------|
| Send email | Yes | Yes | Yes | Yes |
| **File attachments** | **Yes** | **No** | Yes | Yes |
| CLI interface | Yes | Yes | No | No |
| OAuth2 (no passwords) | Yes | Yes | No (SMTP) | Yes |
| Read inbox | Yes | Yes | No | Yes |
| JSON output | Yes | Yes | No | No |
| Python library | Yes | No (Rust) | Yes | Yes |
| Maintained (2026) | **Active** | Active | **Inactive** | Low |

## How It Works

gmsend uses the [Gmail API](https://developers.google.com/gmail/api) via Google's official Python client libraries. Authentication is handled through OAuth2 with a local browser flow — no SMTP passwords or app-specific passwords needed.

Under the hood:
1. **Auth** — `google-auth-oauthlib` handles the OAuth2 flow, tokens are saved locally
2. **MIME** — Python's `email.mime` builds multipart messages with attachments
3. **Send** — `google-api-python-client` calls the Gmail API to send the message
4. **CLI** — `typer` provides the command-line interface with auto-generated help

## Origin Story

We needed to send court filings as PDF attachments via Gmail from a CLI script. Google's official Workspace CLI (`gws`) couldn't do it — no attachment support. We [filed an issue](https://github.com/googleworkspace/cli/issues/498). It's still open. So we built gmsend.

## Contributing

Contributions welcome! Please open an issue first to discuss what you'd like to change.

```bash
git clone https://github.com/alimpolat/gmsend.git
cd gmsend
pip install -e ".[dev]"
pytest tests/
```

## License

[MIT](LICENSE)
