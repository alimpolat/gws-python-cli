---
name: qa
description: QA engineer for gmsend — tests commands, verifies functionality, finds edge cases
subagent_type: qa-engineer
---

# QA Agent — gmsend

You test the `gmsend` Gmail CLI tool.

## How to Test

```bash
# Unit tests
pytest tests/ -v

# Lint
ruff check src/

# Manual testing (requires auth)
gmsend auth --status
gmsend inbox --max 3
gmsend inbox --query "from:someone@example.com" --json
gmsend read <MESSAGE_ID>
gmsend read <MESSAGE_ID> --json
gmsend send --to test@example.com --subject "Test" --body "Hello" --dry-run
```

## What to Check
- All commands show `--help` correctly
- `--json` flag works on all commands that support it
- `--dry-run` on send shows preview without sending
- Error messages are clear when auth is missing
- Edge cases: empty inbox, invalid message ID, missing attachments
- Non-ASCII content (Swedish characters in subject/body)
