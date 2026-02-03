#!/usr/bin/env python3
"""
Monica CRM API Client - Optimized Version (using requests)

Provides a simple interface to interact with Monica Personal CRM API.
Automatically loads configuration from .env file in the project root.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Try to use requests, fall back to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import urllib.request
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class MonicaAPIError(Exception):
    """Base exception for Monica API errors."""
    pass


def load_env_from_file(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file (default: searches in current and parent directories)

    Returns:
        Dict of environment variables
    """
    if env_path is None:
        # Search for .env in current directory and parent directories
        current_dir = Path.cwd()
        for parent in [current_dir, *current_dir.parents]:
            potential_env = parent / '.env'
            if potential_env.exists():
                env_path = str(potential_env)
                break

    if not env_path or not Path(env_path).exists():
        return {}

    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


class MonicaAPI:
    """Monica Personal CRM API Client with .env support."""

    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None,
                 env_path: Optional[str] = None):
        """
        Initialize the Monica API client.

        Args:
            api_url: Monica API base URL (default: from .env or MONICA_API_URL env)
            api_token: Monica API token (default: from .env or MONICA_API_TOKEN env)
            env_path: Path to .env file (default: auto-detect)
        """
        # Load from .env file
        env_vars = load_env_from_file(env_path)

        # Get API URL - remove /api suffix if present to avoid duplication
        url_source = api_url or os.environ.get('MONICA_API_URL') or env_vars.get('MONICA_API_URL') or env_vars.get('MONICA_BASE_URL')
        if url_source:
            self.api_url = url_source.rstrip('/').replace('/api', '')
        else:
            self.api_url = 'https://app.monicahq.com'

        # Get API token
        self.api_token = (api_token or
                         os.environ.get('MONICA_API_TOKEN') or
                         env_vars.get('MONICA_API_TOKEN'))

        if not self.api_token:
            raise MonicaAPIError(
                "MONICA_API_TOKEN not found in .env file or environment variables. "
                "Please create a .env file with MONICA_API_TOKEN=your_token_here"
            )

        self.session = None
        # Prefer urllib as it's more reliable with this API
        self.use_requests = False  # Set to True to try requests instead
        if HAS_REQUESTS:
            # We'll use requests directly instead of Session to avoid potential issues
            self.default_headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Monica API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., '/contacts')
            data: Request body data for POST/PUT
            params: Query parameters for GET requests

        Returns:
            JSON response as a dictionary
        """
        url = f"{self.api_url}/api{endpoint}"

        if self.use_requests:
            # Use requests library directly
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self.default_headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                raise MonicaAPIError(f"Request error: {e}") from e
        else:
            # Fall back to urllib
            if params:
                url += f"?{urlencode(params)}"

            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            body = None
            if data:
                body = json.dumps(data).encode('utf-8')

            req = Request(url, data=body, headers=headers, method=method)

            try:
                with urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode('utf-8'))
            except HTTPError as e:
                error_body = e.read().decode('utf-8')
                raise MonicaAPIError(f"HTTP {e.code}: {error_body}") from e
            except URLError as e:
                raise MonicaAPIError(f"Connection error: {e.reason}") from e

    # ========== CONTACTS ==========

    def list_contacts(self, limit: int = 10, page: int = 1,
                      query: Optional[str] = None, sort: Optional[str] = None) -> Dict:
        """
        List all contacts.

        Args:
            limit: Page size (default: 10)
            page: Page number (default: 1)
            query: Search query string
            sort: Sort field (created_at, -created_at, updated_at, -updated_at)

        Returns:
            Dict with contacts data and pagination info
        """
        params = {'limit': limit, 'page': page}
        if query:
            params['query'] = query
        if sort:
            params['sort'] = sort
        return self._request('GET', '/contacts', params=params)

    def find_contact(self, name: str, limit: int = 50) -> Optional[Dict]:
        """
        Find a contact by name.

        Args:
            name: Contact name to search for
            limit: Maximum results to return

        Returns:
            Contact dict if found, None otherwise
        """
        result = self.list_contacts(limit=limit, query=name)
        if result.get('data'):
            for contact in result['data']:
                full_name = contact.get('complete_name', '')
                first_name = contact.get('first_name', '')
                last_name = contact.get('last_name', '')
                if (name.lower() in full_name.lower() or
                    name.lower() in first_name.lower() or
                    name.lower() in (last_name or '').lower()):
                    return contact
        return None

    def get_contact(self, contact_id: int, with_fields: bool = False) -> Dict:
        """
        Get a specific contact.

        Args:
            contact_id: Contact ID
            with_fields: Include contact fields in response

        Returns:
            Contact data
        """
        endpoint = f"/contacts/{contact_id}"
        if with_fields:
            params = {'with': 'contactfields'}
            return self._request('GET', endpoint, params=params)
        return self._request('GET', endpoint)

    def create_contact(self, first_name: str, gender_id: int,
                       last_name: Optional[str] = None,
                       nickname: Optional[str] = None,
                       birthdate_day: Optional[int] = None,
                       birthdate_month: Optional[int] = None,
                       birthdate_year: Optional[int] = None,
                       is_birthdate_known: bool = False,
                       birthdate_is_age_based: bool = False,
                       birthdate_age: Optional[int] = None,
                       is_partial: bool = False,
                       is_deceased: bool = False,
                       **kwargs) -> Dict:
        """
        Create a new contact.

        Args:
            first_name: First name (required)
            gender_id: Gender ID (1=Male, 2=Female, 3=Non-binary, 4=Other)
            last_name: Last name
            nickname: Nickname
            birthdate_day: Birthdate day
            birthdate_month: Birthdate month
            birthdate_year: Birthdate year
            is_birthdate_known: Whether birthdate is known
            birthdate_is_age_based: Whether birthdate is age-based
            birthdate_age: Age if birthdate is age-based
            is_partial: Whether contact is partial (relationship)
            is_deceased: Whether contact is deceased
            **kwargs: Additional fields

        Returns:
            Created contact data
        """
        data = {
            'first_name': first_name,
            'gender_id': gender_id,
            'is_birthdate_known': is_birthdate_known,
            'is_deceased_date_known': False,
            'is_partial': is_partial,
            'is_deceased': is_deceased,
        }

        if last_name is not None:
            data['last_name'] = last_name
        if nickname is not None:
            data['nickname'] = nickname
        if birthdate_day is not None:
            data['birthdate_day'] = birthdate_day
        if birthdate_month is not None:
            data['birthdate_month'] = birthdate_month
        if birthdate_year is not None:
            data['birthdate_year'] = birthdate_year
        if birthdate_is_age_based:
            data['birthdate_is_age_based'] = birthdate_is_age_based
        if birthdate_age is not None:
            data['birthdate_age'] = birthdate_age

        data.update(kwargs)
        result = self._request('POST', '/contacts', data=data)

        # Handle response format - may be wrapped in 'data' key
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list):
                if len(data_obj) == 0:
                    return result
                # Try to find the contact we just created
                for contact in reversed(data_obj):
                    if contact.get('first_name') == first_name:
                        return contact
                # If not found in list, the POST may have been redirected to GET
                # Return first contact as fallback (or could raise error)
                return data_obj[-1]
        return result

    def find_or_create_contact(self, first_name: str, gender_id: int = 1,
                               last_name: Optional[str] = None,
                               search_name: Optional[str] = None) -> Tuple[Dict, bool]:
        """
        Find an existing contact or create a new one.

        Args:
            first_name: First name
            gender_id: Gender ID (default: 1=Male)
            last_name: Last name
            search_name: Name to search for (default: first_name + last_name)

        Returns:
            Tuple of (contact dict, created: bool)
        """
        name_to_search = search_name or f"{first_name} {last_name or ''}".strip()
        existing = self.find_contact(name_to_search)

        if existing:
            return existing, False

        new_contact = self.create_contact(
            first_name=first_name,
            gender_id=gender_id,
            last_name=last_name
        )
        return new_contact, True

    def update_contact(self, contact_id: int, **kwargs) -> Dict:
        """
        Update an existing contact.

        Args:
            contact_id: Contact ID
            **kwargs: Fields to update

        Returns:
            Updated contact data
        """
        # Monica API requires certain fields when updating
        # Get current contact data first to get required fields
        current = self.get_contact(contact_id, with_fields=True)
        contact_data = current.get('data', current)

        # Build update data with required fields
        update_data = {
            'first_name': contact_data.get('first_name', ''),
            'gender_id': contact_data.get('gender_id', 1),
            'is_birthdate_known': contact_data.get('information', {}).get('dates', {}).get('birthdate', {}).get('is_age_based') or False,
            'is_deceased_date_known': contact_data.get('information', {}).get('dates', {}).get('deceased_date', {}).get('is_age_based') or False,
            'is_partial': contact_data.get('is_partial', False),
            'is_deceased': contact_data.get('is_dead', False),
        }
        update_data.update(kwargs)

        return self._request('PUT', f'/contacts/{contact_id}', data=update_data)

    def delete_contact(self, contact_id: int) -> Dict:
        """
        Delete a contact.

        Args:
            contact_id: Contact ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/contacts/{contact_id}')

    def get_contact_notes(self, contact_id: int, limit: int = 10, page: int = 1) -> Dict:
        """Get notes for a specific contact."""
        return self._request('GET', f'/contacts/{contact_id}/notes',
                           params={'limit': limit, 'page': page})

    def get_contact_activities(self, contact_id: int, limit: int = 10, page: int = 1) -> Dict:
        """Get activities for a specific contact."""
        return self._request('GET', f'/contacts/{contact_id}/activities',
                           params={'limit': limit, 'page': page})

    # ========== CONTACT FIELDS ==========

    def set_contact_field(self, contact_id: int, field_type: str,
                         value: str, is_favorite: bool = False) -> Dict:
        """
        Set a contact field (phone, email, address, etc.).

        Args:
            contact_id: Contact ID
            field_type: Field type (e.g., 'phone', 'email', 'address')
            value: Field value
            is_favorite: Mark as favorite

        Returns:
            Created field data
        """
        # Monica API uses POST /contactfields with contact_id in body
        data = {
            'contact_id': contact_id,
            'contact_field_type': field_type,
            'data': value,
            'is_favorite': 1 if is_favorite else 0
        }
        return self._request('POST', '/contactfields', data=data)

    def update_contact_field(self, field_id: int, value: str, is_favorite: Optional[bool] = None) -> Dict:
        """
        Update an existing contact field.

        Args:
            field_id: Contact field ID
            value: New field value
            is_favorite: Mark as favorite (optional)

        Returns:
            Updated field data
        """
        data = {'data': value}
        if is_favorite is not None:
            data['is_favorite'] = 1 if is_favorite else 0
        return self._request('PUT', f'/contactfields/{field_id}', data=data)

    def delete_contact_field(self, field_id: int) -> Dict:
        """
        Delete a contact field.

        Args:
            field_id: Contact field ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/contactfields/{field_id}')

    # ========== NOTES ==========

    def list_notes(self, limit: int = 10, page: int = 1) -> Dict:
        """List all notes."""
        return self._request('GET', '/notes', params={'limit': limit, 'page': page})

    def get_note(self, note_id: int) -> Dict:
        """Get a specific note."""
        return self._request('GET', f'/notes/{note_id}')

    def create_note(self, body: str, contact_id: int, is_favorited: bool = False) -> Dict:
        """
        Create a new note.

        Args:
            body: Note content (required)
            contact_id: Associated contact ID (required)
            is_favorited: Whether to favorite the note

        Returns:
            Created note data
        """
        data = {
            'body': body,
            'contact_id': contact_id,
            'is_favorited': 1 if is_favorited else 0
        }
        result = self._request('POST', '/notes', data=data)
        # Handle response format - may be wrapped in 'data' key
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_note(self, note_id: int, **kwargs) -> Dict:
        """Update an existing note."""
        return self._request('PUT', f'/notes/{note_id}', data=kwargs)

    def delete_note(self, note_id: int) -> Dict:
        """Delete a note."""
        return self._request('DELETE', f'/notes/{note_id}')

    # ========== ACTIVITIES ==========

    def list_activities(self, limit: int = 10, page: int = 1) -> Dict:
        """List all activities."""
        return self._request('GET', '/activities', params={'limit': limit, 'page': page})

    def get_activity(self, activity_id: int) -> Dict:
        """Get a specific activity."""
        return self._request('GET', f'/activities/{activity_id}')

    def create_activity(self, activity_type_id: int, summary: str, happened_at: str,
                        contacts: List[int], description: Optional[str] = None,
                        emotions: Optional[List[int]] = None) -> Dict:
        """
        Create a new activity.

        Args:
            activity_type_id: Activity type ID (required)
            summary: Short description (required)
            happened_at: Date of activity (YYYY-MM-DD format, required)
            contacts: List of contact IDs (required)
            description: Optional detailed description
            emotions: Optional list of emotion IDs

        Returns:
            Created activity data
        """
        data = {
            'activity_type_id': activity_type_id,
            'summary': summary,
            'happened_at': happened_at,
            'contacts': contacts
        }
        if description:
            data['description'] = description
        if emotions:
            data['emotions'] = emotions
        result = self._request('POST', '/activities', data=data)
        # Handle response format - may be wrapped in 'data' key
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_activity(self, activity_id: int, **kwargs) -> Dict:
        """Update an existing activity."""
        return self._request('PUT', f'/activities/{activity_id}', data=kwargs)

    def delete_activity(self, activity_id: int) -> Dict:
        """Delete an activity."""
        return self._request('DELETE', f'/activities/{activity_id}')

    # ========== TASKS ==========

    def list_tasks(self, limit: int = 10, page: int = 1) -> Dict:
        """List all tasks."""
        return self._request('GET', '/tasks', params={'limit': limit, 'page': page})

    def get_task(self, task_id: int) -> Dict:
        """Get a specific task."""
        return self._request('GET', f'/tasks/{task_id}')

    def create_task(self, title: str, due_date: str, contact_id: Optional[int] = None, **kwargs) -> Dict:
        """
        Create a new task.

        Args:
            title: Task title (required)
            due_date: Due date (YYYY-MM-DD format, required)
            contact_id: Associated contact ID
            **kwargs: Additional fields

        Returns:
            Created task data
        """
        data = {
            'title': title,
            'due_date': due_date
        }
        if contact_id:
            data['contact_id'] = contact_id
        data.update(kwargs)
        result = self._request('POST', '/tasks', data=data)
        # Handle response format
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_task(self, task_id: int, **kwargs) -> Dict:
        """
        Update an existing task.

        Args:
            task_id: Task ID
            **kwargs: Fields to update

        Returns:
            Updated task data
        """
        return self._request('PUT', f'/tasks/{task_id}', data=kwargs)

    def delete_task(self, task_id: int) -> Dict:
        """
        Delete a task.

        Args:
            task_id: Task ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/tasks/{task_id}')

    # ========== REMINDERS ==========

    def list_reminders(self, limit: int = 10, page: int = 1) -> Dict:
        """List all reminders."""
        return self._request('GET', '/reminders', params={'limit': limit, 'page': page})

    def get_reminder(self, reminder_id: int) -> Dict:
        """Get a specific reminder."""
        result = self._request('GET', f'/reminders/{reminder_id}')
        # Handle response format
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def create_reminder(self, title: str, date: str, contact_id: Optional[int] = None, **kwargs) -> Dict:
        """
        Create a new reminder.

        Args:
            title: Reminder title (required)
            date: Reminder date (YYYY-MM-DD format, required)
            contact_id: Associated contact ID
            **kwargs: Additional fields

        Returns:
            Created reminder data
        """
        data = {
            'title': title,
            'initial_date': date,
            'next_expected_date': date,
            'frequency_type': 'one_time',
            'frequency_number': 1
        }
        if contact_id:
            data['contact_id'] = contact_id
        data.update(kwargs)
        result = self._request('POST', '/reminders', data=data)
        # Handle response format
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_reminder(self, reminder_id: int, **kwargs) -> Dict:
        """
        Update an existing reminder.

        Args:
            reminder_id: Reminder ID
            **kwargs: Fields to update

        Returns:
            Updated reminder data
        """
        return self._request('PUT', f'/reminders/{reminder_id}', data=kwargs)

    def delete_reminder(self, reminder_id: int) -> Dict:
        """
        Delete a reminder.

        Args:
            reminder_id: Reminder ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/reminders/{reminder_id}')

    # ========== TAGS ==========

    def list_tags(self, limit: int = 10, page: int = 1) -> Dict:
        """List all tags."""
        return self._request('GET', '/tags', params={'limit': limit, 'page': page})

    def get_tag_contacts(self, tag_id: int, limit: int = 10, page: int = 1) -> Dict:
        """Get contacts for a specific tag."""
        return self._request('GET', f'/tags/{tag_id}/contacts',
                           params={'limit': limit, 'page': page})

    def create_tag(self, name: str) -> Dict:
        """
        Create a new tag.

        Args:
            name: Tag name (required)

        Returns:
            Created tag data
        """
        data = {'name': name}
        result = self._request('POST', '/tags', data=data)
        # Handle response format
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_tag(self, tag_id: int, name: str) -> Dict:
        """
        Update an existing tag.

        Args:
            tag_id: Tag ID
            name: New tag name

        Returns:
            Updated tag data
        """
        data = {'name': name}
        return self._request('PUT', f'/tags/{tag_id}', data=data)

    def delete_tag(self, tag_id: int) -> Dict:
        """
        Delete a tag.

        Args:
            tag_id: Tag ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/tags/{tag_id}')

    def set_contact_tags(self, contact_id: int, tags: List[str]) -> Dict:
        """
        Set tags for a contact (replaces all existing tags).

        Args:
            contact_id: Contact ID
            tags: List of tag names to set

        Returns:
            Updated contact data
        """
        import requests
        url = f"{self.api_url}/api/contacts/{contact_id}/setTags"
        data = {'tags': tags}
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        try:
            if HAS_REQUESTS:
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return response.json()
            else:
                import urllib.request
                body = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=body, headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=60) as response:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise MonicaAPIError(f"Failed to set tags: {e}") from e

    # ========== CONVERSATIONS ==========

    def list_conversations(self, limit: int = 10, page: int = 1) -> Dict:
        """List all conversations."""
        return self._request('GET', '/conversations', params={'limit': limit, 'page': page})

    def list_contact_conversations(self, contact_id: int, limit: int = 10, page: int = 1) -> Dict:
        """List all conversations for a specific contact."""
        return self._request('GET', f'/contacts/{contact_id}/conversations',
                           params={'limit': limit, 'page': page})

    def get_conversation(self, conversation_id: int) -> Dict:
        """Get a specific conversation."""
        return self._request('GET', f'/conversations/{conversation_id}')

    def create_conversation(self, contact_id: int, contact_field_type_id: int, happened_at: str, **kwargs) -> Dict:
        """
        Create a new conversation.

        Args:
            contact_id: Contact ID (required)
            contact_field_type_id: Contact field type ID (required)
            happened_at: When the conversation happened (required, ISO format)
            **kwargs: Additional fields

        Returns:
            Created conversation data
        """
        data = {
            'contact_id': contact_id,
            'contact_field_type_id': contact_field_type_id,
            'happened_at': happened_at
        }
        data.update(kwargs)
        result = self._request('POST', '/conversations', data=data)
        # Handle response format
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_conversation(self, conversation_id: int, **kwargs) -> Dict:
        """
        Update an existing conversation.

        Args:
            conversation_id: Conversation ID
            **kwargs: Fields to update

        Returns:
            Updated conversation data
        """
        return self._request('PUT', f'/conversations/{conversation_id}', data=kwargs)

    def delete_conversation(self, conversation_id: int) -> Dict:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/conversations/{conversation_id}')

    def add_message_to_conversation(self, conversation_id: int, content: str, 
                                  written_at: str, written_by_me: bool = True, **kwargs) -> Dict:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID (required)
            content: Message content (required)
            written_at: When the message was written (required, ISO format)
            written_by_me: Whether the message was written by me (default: True)
            **kwargs: Additional fields

        Returns:
            Created message data
        """
        data = {
            'content': content,
            'written_at': written_at,
            'written_by_me': 1 if written_by_me else 0
        }
        data.update(kwargs)
        result = self._request('POST', f'/conversations/{conversation_id}/messages', data=data)
        # Handle response format
        if isinstance(result, dict):
            data_obj = result.get('data', result)
            if isinstance(data_obj, dict):
                return data_obj
            elif isinstance(data_obj, list) and len(data_obj) > 0:
                return data_obj[0]
        return result

    def update_message(self, message_id: int, content: str, **kwargs) -> Dict:
        """
        Update a message in a conversation.

        Args:
            message_id: Message ID
            content: New message content
            **kwargs: Additional fields

        Returns:
            Updated message data
        """
        data = {'content': content}
        data.update(kwargs)
        return self._request('PUT', f'/messages/{message_id}', data=data)

    def delete_message(self, message_id: int) -> Dict:
        """
        Delete a message.

        Args:
            message_id: Message ID

        Returns:
            Deletion response
        """
        return self._request('DELETE', f'/messages/{message_id}')


def main():
    """CLI interface for Monica API."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Monica CRM API CLI - Automatically loads from .env',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List contacts
  python monica_api.py contacts

  # Add a new contact with phone
  python monica_api.py add-contact "John Doe" --phone "1234567890" --note "New client"

  # Find or create contact
  python monica_api.py find-or-create "Jane Smith" --phone "9876543210"
        """
    )

    parser.add_argument('--env', help='Path to .env file (default: auto-detect)')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Contacts command
    contacts_parser = subparsers.add_parser('contacts', help='List contacts')
    contacts_parser.add_argument('--limit', type=int, default=15)
    contacts_parser.add_argument('--page', type=int, default=1)
    contacts_parser.add_argument('--query', help='Search query')
    contacts_parser.add_argument('--sort', help='Sort field')

    # Find contact
    find_parser = subparsers.add_parser('find', help='Find a contact by name')
    find_parser.add_argument('name', help='Name to search for')

    # Get contact
    get_parser = subparsers.add_parser('get', help='Get a contact')
    get_parser.add_argument('id', type=int, help='Contact ID')
    get_parser.add_argument('--with-fields', action='store_true')

    # Add contact (convenience command)
    add_parser = subparsers.add_parser('add-contact', help='Add a new contact with details')
    add_parser.add_argument('name', help='Contact name (first name or "First Last")')
    add_parser.add_argument('--phone', help='Phone number')
    add_parser.add_argument('--email', help='Email address')
    add_parser.add_argument('--note', help='Add a note to the contact')
    add_parser.add_argument('--gender', type=int, default=1,
                           choices=[1, 2, 3, 4],
                           help='Gender (1=Male, 2=Female, 3=Non-binary, 4=Other)')

    # Find or create contact
    foc_parser = subparsers.add_parser('find-or-create', help='Find existing or create new contact')
    foc_parser.add_argument('name', help='Contact name')
    foc_parser.add_argument('--phone', help='Phone number')
    foc_parser.add_argument('--note', help='Note to add')

    # Create note
    note_parser = subparsers.add_parser('add-note', help='Add a note to a contact')
    note_parser.add_argument('contact_id', type=int, help='Contact ID')
    note_parser.add_argument('body', help='Note content')

    # Tasks commands
    tasks_parser = subparsers.add_parser('tasks', help='Manage tasks')
    tasks_subparsers = tasks_parser.add_subparsers(dest='tasks_command', help='Task subcommands')
    
    task_list_parser = tasks_subparsers.add_parser('list', help='List tasks')
    task_list_parser.add_argument('--limit', type=int, default=10)
    task_list_parser.add_argument('--page', type=int, default=1)
    
    task_create_parser = tasks_subparsers.add_parser('create', help='Create a task')
    task_create_parser.add_argument('title', help='Task title')
    task_create_parser.add_argument('due_date', help='Due date (YYYY-MM-DD)')
    task_create_parser.add_argument('--contact-id', type=int, help='Contact ID')
    
    task_delete_parser = tasks_subparsers.add_parser('delete', help='Delete a task')
    task_delete_parser.add_argument('task_id', type=int, help='Task ID')

    # Reminders commands
    reminders_parser = subparsers.add_parser('reminders', help='Manage reminders')
    reminders_subparsers = reminders_parser.add_subparsers(dest='reminders_command', help='Reminder subcommands')
    
    reminder_list_parser = reminders_subparsers.add_parser('list', help='List reminders')
    reminder_list_parser.add_argument('--limit', type=int, default=10)
    reminder_list_parser.add_argument('--page', type=int, default=1)
    
    reminder_create_parser = reminders_subparsers.add_parser('create', help='Create a reminder')
    reminder_create_parser.add_argument('title', help='Reminder title')
    reminder_create_parser.add_argument('date', help='Reminder date (YYYY-MM-DD)')
    reminder_create_parser.add_argument('--contact-id', type=int, help='Contact ID')
    
    reminder_delete_parser = reminders_subparsers.add_parser('delete', help='Delete a reminder')
    reminder_delete_parser.add_argument('reminder_id', type=int, help='Reminder ID')

    # Tags commands
    tags_parser = subparsers.add_parser('tags', help='Manage tags')
    tags_subparsers = tags_parser.add_subparsers(dest='tags_command', help='Tag subcommands')
    
    tag_list_parser = tags_subparsers.add_parser('list', help='List tags')
    tag_list_parser.add_argument('--limit', type=int, default=10)
    tag_list_parser.add_argument('--page', type=int, default=1)
    
    tag_create_parser = tags_subparsers.add_parser('create', help='Create a tag')
    tag_create_parser.add_argument('name', help='Tag name')
    
    tag_delete_parser = tags_subparsers.add_parser('delete', help='Delete a tag')
    tag_delete_parser.add_argument('tag_id', type=int, help='Tag ID')

    tag_set_parser = tags_subparsers.add_parser('set', help='Set tags for a contact')
    tag_set_parser.add_argument('contact_id', type=int, help='Contact ID')
    tag_set_parser.add_argument('tags', nargs='+', help='Tag names to set (space-separated)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        api = MonicaAPI(env_path=args.env)

        if args.command == 'contacts':
            result = api.list_contacts(limit=args.limit, page=args.page,
                                      query=args.query, sort=args.sort)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'find':
            result = api.find_contact(args.name)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"No contact found matching: {args.name}")
                sys.exit(1)

        elif args.command == 'get':
            result = api.get_contact(args.id, with_fields=args.with_fields)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'add-contact':
            # Parse name
            parts = args.name.split()
            first_name = parts[0]
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else None

            contact, created = api.find_or_create_contact(
                first_name=first_name,
                last_name=last_name,
                gender_id=args.gender
            )

            if created:
                print(f"✓ Created new contact: {contact['complete_name']} (ID: {contact['id']})")
            else:
                print(f"✓ Found existing contact: {contact['complete_name']} (ID: {contact['id']})")

            # Add phone if provided (as note for now, until we get field type IDs)
            if args.phone:
                phone_note = f"电话: {args.phone}"
                if args.note:
                    phone_note = args.note + "\n" + phone_note
                    args.note = phone_note  # Update note to include phone
                else:
                    args.note = phone_note

            # Add email if provided (as note for now)
            if args.email:
                email_note = f"邮箱: {args.email}"
                if args.note:
                    args.note = args.note + "\n" + email_note
                else:
                    args.note = email_note

            # Add note if provided
            if args.note:
                api.create_note(body=args.note, contact_id=contact['id'])
                print(f"  ✓ Added note: {args.note}")

        elif args.command == 'find-or-create':
            parts = args.name.split()
            first_name = parts[0]
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else None

            contact, created = api.find_or_create_contact(
                first_name=first_name,
                last_name=last_name
            )

            if created:
                print(f"✓ Created: {contact['complete_name']} (ID: {contact['id']})")
            else:
                print(f"✓ Found: {contact['complete_name']} (ID: {contact['id']})")

            # Add phone if provided (as note for now, until we get field type IDs)
            if args.phone:
                phone_note = f"电话: {args.phone}"
                if args.note:
                    phone_note = args.note + "\n" + phone_note
                    args.note = phone_note  # Update note to include phone
                else:
                    args.note = phone_note

            # Add note if provided
            if args.note:
                api.create_note(body=args.note, contact_id=contact['id'])
                print(f"  ✓ Note: {args.note}")

        elif args.command == 'add-note':
            result = api.create_note(body=args.body, contact_id=args.contact_id)
            print(f"✓ Note added to contact {args.contact_id}")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        # Tasks commands
        elif args.command == 'tasks':
            if args.tasks_command == 'list':
                result = api.list_tasks(limit=args.limit, page=args.page)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.tasks_command == 'create':
                result = api.create_task(
                    title=args.title,
                    due_date=args.due_date,
                    contact_id=getattr(args, 'contact_id', None)
                )
                print(f"✓ Task created: {result['title']} (ID: {result['id']})")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.tasks_command == 'delete':
                result = api.delete_task(task_id=args.task_id)
                print(f"✓ Task {args.task_id} deleted")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                tasks_parser.print_help()
                sys.exit(1)

        # Reminders commands
        elif args.command == 'reminders':
            if args.reminders_command == 'list':
                result = api.list_reminders(limit=args.limit, page=args.page)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.reminders_command == 'create':
                result = api.create_reminder(
                    title=args.title,
                    date=args.date,
                    contact_id=getattr(args, 'contact_id', None)
                )
                print(f"✓ Reminder created: {result['title']} (ID: {result['id']})")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.reminders_command == 'delete':
                result = api.delete_reminder(reminder_id=args.reminder_id)
                print(f"✓ Reminder {args.reminder_id} deleted")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                reminders_parser.print_help()
                sys.exit(1)

        # Tags commands
        elif args.command == 'tags':
            if args.tags_command == 'list':
                result = api.list_tags(limit=args.limit, page=args.page)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.tags_command == 'create':
                result = api.create_tag(name=args.name)
                print(f"✓ Tag created: {result['name']} (ID: {result['id']})")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.tags_command == 'delete':
                result = api.delete_tag(tag_id=args.tag_id)
                print(f"✓ Tag {args.tag_id} deleted")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.tags_command == 'set':
                result = api.set_contact_tags(contact_id=args.contact_id, tags=args.tags)
                print(f"✓ Set tags for contact {args.contact_id}: {', '.join(args.tags)}")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                tags_parser.print_help()
                sys.exit(1)

        else:
            parser.print_help()
            sys.exit(1)

    except MonicaAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
