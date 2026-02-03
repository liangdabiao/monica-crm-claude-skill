# Monica CRM API Reference

This reference document contains the complete Monica CRM API documentation for quick lookup.

## Table of Contents

- [Authentication](#authentication)
- [Contacts](#contacts)
- [Notes](#notes)
- [Activities](#activities)
- [Tasks](#tasks)
- [Reminders](#reminders)
- [Tags](#tags)

---

## Authentication

All API requests require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

Base URL: `https://app.monicahq.com/api` (or custom instance URL + `/api`)

---

## Contacts

### List all contacts

**GET** `/contacts/`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size (default: 10) |
| page | integer | Page number (default: 1) |
| query | string | Search query |
| sort | string | Sort: `created_at`, `-created_at`, `updated_at`, `-updated_at` |

### Get a specific contact

**GET** `/contacts/:id`

Add `?with=contactfields` to include contact fields.

### Create a contact

**POST** `/contacts/`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| first_name | string | Yes | Max 50 chars |
| last_name | string | No | Max 100 chars |
| nickname | string | No | Max 100 chars |
| gender_id | integer | Yes | Gender ID from API |
| birthdate_day | integer | Conditional | Day if birthdate known |
| birthdate_month | integer | Conditional | Month if birthdate known |
| birthdate_year | integer | No | Year of birthdate |
| is_birthdate_known | boolean | Yes | Whether birthdate is known |
| birthdate_is_age_based | boolean | No | If birthdate based on age |
| birthdate_age | integer | Conditional | Age if age-based |
| is_partial | boolean | Yes | Real (false) or partial (true) contact |
| is_deceased | boolean | Yes | Whether deceased |
| deceased_date_day | integer | No | Deceased day |
| deceased_date_month | integer | No | Deceased month |
| deceased_date_year | integer | No | Deceased year |
| is_deceased_date_known | boolean | Yes | Whether deceased date known |

### Update a contact

**PUT** `/contacts/:id`

Same fields as create, all optional.

### Delete a contact

**DELETE** `/contacts/:id`

---

## Notes

### List all notes

**GET** `/notes/`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size |
| page | integer | Page number |

### List notes for a contact

**GET** `/contacts/:id/notes`

### Get a specific note

**GET** `/notes/:id`

### Create a note

**POST** `/notes/`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| body | string | Yes | Max 100000 chars |
| contact_id | integer | Yes | Associated contact ID |
| is_favorited | integer | Yes | 0 or 1 |

### Update a note

**PUT** `/notes/:id`

Same fields as create, all optional.

### Delete a note

**DELETE** `/notes/:id`

---

## Activities

### List all activities

**GET** `/activities/`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size |
| page | integer | Page number |

### List activities for a contact

**GET** `/contacts/:id/activities`

### Get a specific activity

**GET** `/activities/:id`

### Create an activity

**POST** `/activities/`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| activity_type_id | integer | Yes | Activity type ID |
| summary | string | Yes | Max 255 chars |
| description | string | No | Max 1000000 chars |
| happened_at | string | Yes | YYYY-MM-DD format |
| contacts | array | Yes | Array of contact IDs |
| emotions | array | No | Array of emotion IDs |

### Update an activity

**PUT** `/activities/:id`

Same fields as create, all optional.

### Delete an activity

**DELETE** `/activities/:id`

---

## Tasks

### List all tasks

**GET** `/tasks/`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size |
| page | integer | Page number |

### Get a specific task

**GET** `/tasks/:id`

---

## Reminders

### List all reminders

**GET** `/reminders/`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size |
| page | integer | Page number |

### Get a specific reminder

**GET** `/reminders/:id`

---

## Tags

### List all tags

**GET** `/tags/`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size |
| page | integer | Page number |

### Get contacts for a tag

**GET** `/tags/:id/contacts`

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Page size |
| page | integer | Page number |

---

## Response Format

All responses follow this structure:

```json
{
  "data": [...],
  "links": {
    "first": "...",
    "last": "...",
    "prev": "...",
    "next": "..."
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 10,
    "per_page": "10",
    "to": 10,
    "total": 100
  }
}
```

Single item responses:

```json
{
  "data": {
    "id": 1,
    "object": "contact",
    ...
  }
}
```
