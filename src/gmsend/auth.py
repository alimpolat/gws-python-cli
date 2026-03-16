"""OAuth2 authentication for Gmail API."""
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]

CONFIG_DIR = Path.home() / ".config" / "gmsend"
CLIENT_SECRET_FILE = CONFIG_DIR / "client_secret.json"
TOKEN_FILE = CONFIG_DIR / "token.json"


def get_config_dir() -> Path:
    """Return the config directory, creating it if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def has_client_secret() -> bool:
    """Check if a client_secret.json exists."""
    return CLIENT_SECRET_FILE.exists()


def has_token() -> bool:
    """Check if an auth token exists."""
    return TOKEN_FILE.exists()


def get_auth_status() -> dict:
    """Return current authentication status."""
    status = {
        "config_dir": str(CONFIG_DIR),
        "client_secret": has_client_secret(),
        "token": has_token(),
        "authenticated": False,
        "email": None,
    }

    if has_token():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            status["authenticated"] = creds.valid or (creds.expired and creds.refresh_token)
            if creds.valid or (creds.expired and creds.refresh_token):
                if creds.expired:
                    creds.refresh(Request())
                service = build("gmail", "v1", credentials=creds)
                profile = service.users().getProfile(userId="me").execute()
                status["email"] = profile.get("emailAddress")
                status["authenticated"] = True
        except Exception:
            status["authenticated"] = False

    return status


def authenticate() -> Credentials:
    """Run OAuth2 authentication flow. Opens browser for consent."""
    get_config_dir()

    if not has_client_secret():
        raise FileNotFoundError(
            f"No client_secret.json found at {CLIENT_SECRET_FILE}\n\n"
            "Setup:\n"
            "  1. Go to https://console.cloud.google.com/apis/credentials\n"
            "  2. Create an OAuth 2.0 Client ID (Desktop app)\n"
            "  3. Download the JSON and save it to:\n"
            f"     {CLIENT_SECRET_FILE}\n"
            "  4. Enable the Gmail API:\n"
            "     https://console.cloud.google.com/apis/library/gmail.googleapis.com\n"
            "  5. Add your email as a test user in the OAuth consent screen\n"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json())
    return creds


def get_credentials() -> Credentials:
    """Get valid credentials, refreshing or re-authenticating as needed."""
    creds = None

    if has_token():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json())
        else:
            creds = authenticate()

    return creds


def get_gmail_service():
    """Return an authenticated Gmail API service."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)
