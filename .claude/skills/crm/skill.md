---
name: crm
description: "Monica Personal CRM integration for managing contacts, notes, activities, tasks, and reminders. Use when user requests involve creating, reading, updating, or deleting contacts; managing notes; logging activities; creating tasks or reminders; working with tags; or any mention of CRM, Monica, or personal relationship management. Automatically loads configuration from .env file."
---

# Monica CRM

Monica Personal CRM API integration for managing contacts, relationships, notes, activities, and more.

## Setup

Create a `.env` file in your project root with:

```env
MONICA_API_TOKEN=your_api_token_here
MONICA_API_URL=https://app.monicahq.com
```

Get your API token from: https://app.monicahq.com/settings

## Quick Start

The script automatically loads configuration from `.env`:

```bash
# List all contacts
python scripts/monica_api.py contacts

# Add a new contact with phone and note
python scripts/monica_api.py add-contact "John Doe" --phone "1234567890" --note "New client"

# Find or create contact
python scripts/monica_api.py find-or-create "Jane Smith" --phone "9876543210"
```

## Core Operations

### Contacts

**List contacts**
```bash
python scripts/monica_api.py contacts --limit 50 --query "john"
```

**Find a contact**
```bash
python scripts/monica_api.py find "John Doe"
```

**Get contact details**
```bash
python scripts/monica_api.py get 123 --with-fields
```

**Add contact** (convenience command - finds or creates)
```bash
python scripts/monica_api.py add-contact "John Doe" --phone "1234567890" --email "john@example.com" --note "Met at conference"
```

**Find or create contact**
```bash
python scripts/monica_api.py find-or-create "Jane Smith" --phone "9876543210" --note "New lead"
```

### Notes

**Add note to contact**
```bash
python scripts/monica_api.py add-note 123 "Had a great lunch meeting today"
```

**Get contact's notes** (via Python import)
```python
from scripts.monica_api import MonicaAPI
api = MonicaAPI()
api.get_contact_notes(123, limit=20)
```

### Activities

**Create activity** (via Python import)
```python
from scripts.monica_api import MonicaAPI
api = MonicaAPI()
api.create_activity(
    activity_type_id=2,
    summary="Lunch meeting",
    description="Discussed project updates",
    happened_at="2025-01-15",
    contacts=[123, 456]
)
```

### Tags

**Add tag to contact** (via Python import)
```python
from scripts.monica_api import MonicaAPI
import urllib.request
import json

api = MonicaAPI()
token = api.api_token
contact_id = 123

# POST /contacts/:id/setTags
url = f'https://app.monicahq.com/api/contacts/{contact_id}/setTags'
data = {'tags': ['欠款人', 'VIP']}
body = json.dumps(data).encode('utf-8')

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

req = urllib.request.Request(url, data=body, headers=headers, method='POST')
with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode('utf-8'))
    # Tag added successfully
```

## Python API

### Basic Usage

```python
from scripts.monica_api import MonicaAPI

# Automatically loads from .env
api = MonicaAPI()
```

### Key Methods

```python
# Contacts
contacts = api.list_contacts(limit=50, query="john")
contact = api.find_contact("John Doe")
contact, created = api.find_or_create_contact("John", "Doe")
new_contact = api.create_contact(first_name="Jane", gender_id=2)

# Contact Fields (phone, email, etc.)
api.set_contact_field(contact_id, 'phone', '1234567890', is_favorite=True)
api.set_contact_field(contact_id, 'email', 'jane@example.com')

# Notes
note = api.create_note(body="Meeting notes", contact_id=123)

# Activities
activity = api.create_activity(
    activity_type_id=2,
    summary="Call with client",
    happened_at="2025-01-15",
    contacts=[123]
)
```

## Common Workflows

### Adding a new client

```bash
python scripts/monica_api.py add-contact "Client Name" \
    --phone "1234567890" \
    --email "client@company.com" \
    --note "Interested in our services"
```

### Recording an interaction

1. Find the contact: `python scripts/monica_api.py find "Client Name"`
2. Add a note: `python scripts/monica_api.py add-note 123 "Discussed Q4 plans"`
3. Optionally log an activity via Python API

### Bulk contact lookup

```bash
# Search for contacts
python scripts/monica_api.py contacts --query "Smith"
```

## Gender IDs

- `1` - Male
- `2` - Female
- `3` - Non-binary
- `4` - Other

## Important Notes

- The script **automatically detects** and loads `.env` file from current or parent directories
- API URL automatically handles `/api` suffix - just use base URL
- All dates use `YYYY-MM-DD` format for activities
- Contact IDs are integers - pass as numbers, not strings
- The `add-contact` command finds existing contacts or creates new ones automatically

## Known Issues & Workarounds

### Notes API Issue (POST /notes/)

**Problem**: The Monica Notes API (`POST /notes/`) has a bug where it returns note data for a different contact than the one specified in `contact_id`. The request succeeds (HTTP 200) but the note is not associated with the intended contact.

**Workaround**: Use the contact's `description` field to store notes instead of the Notes API:

```python
from scripts.monica_api import MonicaAPI
api = MonicaAPI()

# Update contact description (reliable method)
api.update_contact(contact_id, description="欠款1块钱")
```

**Required fields for update_contact()**: When updating a contact, you must include:
- `first_name` (from existing contact)
- `gender_id` (from existing contact)
- `is_birthdate_known` (boolean, usually `False`)
- `is_deceased_date_known` (boolean, usually `False`)
- `is_partial` (from existing contact, usually `False`)
- `is_deceased` (from existing contact, usually `False`)
- Plus any fields you want to update (e.g., `description`)

## Resources

### `scripts/monica_api.py`

Full-featured Python client with .env auto-loading and Cloudflare-compatible headers.

**Key features:**
- Auto-detects and loads `.env` file
- `find_contact()` - Smart contact search
- `find_or_create_contact()` - Idempotent contact creation
- `set_contact_field()` - Add phone, email, address, etc.
- All Monica API endpoints supported

### `references/api.md`

Complete API endpoint reference with all parameters, request formats, and response structures.
