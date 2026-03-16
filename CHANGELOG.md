# Changelog

## [0.1.0] - 2026-03-16

### Added
- `gmsend send` command with `--attach` flag for file attachments
- `gmsend auth` command for OAuth2 setup
- `gmsend inbox` command to list inbox messages
- Support for multiple attachments (`--attach a.pdf --attach b.xlsx`)
- CC and BCC support
- HTML body support (`--html` flag)
- Dry-run mode (`--dry-run`)
- JSON output mode (`--json`)
- Rich terminal output with colors
- Auto-detection of MIME types for any file type
- Token persistence (authenticate once, reuse forever)
