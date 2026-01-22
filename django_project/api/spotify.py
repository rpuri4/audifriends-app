"""
Spotify API client with proper OAuth authentication.

This module handles Spotify API authentication using the Client Credentials flow,
which automatically refreshes the access token when it expires.
"""

import base64
import time
from urllib.parse import quote_plus

import httpx
from django.conf import settings


class SpotifyAuthError(Exception):
    """Raised when Spotify authentication fails."""
    pass


class SpotifyClient:
    """
    Spotify API client with automatic token management.

    Uses the Client Credentials flow for server-to-server authentication.
    Tokens are cached and automatically refreshed when expired.
    """
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE_URL = 'https://api.spotify.com/v1'

    # Class-level token cache
    _token = None
    _token_expires_at = 0

    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET

        if not self.client_id or not self.client_secret:
            raise SpotifyAuthError(
                'Spotify credentials not configured. '
                'Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file.'
            )

    def _get_auth_header(self) -> str:
        """Generate the Basic auth header for token requests."""
        credentials = f'{self.client_id}:{self.client_secret}'
        encoded = base64.b64encode(credentials.encode()).decode()
        return f'Basic {encoded}'

    def _refresh_token(self) -> None:
        """Fetch a new access token from Spotify."""
        with httpx.Client() as client:
            response = client.post(
                self.TOKEN_URL,
                headers={
                    'Authorization': self._get_auth_header(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data={'grant_type': 'client_credentials'},
                timeout=10.0,
            )

            if response.status_code != 200:
                raise SpotifyAuthError(f'Failed to get Spotify token: {response.text}')

            data = response.json()
            SpotifyClient._token = data['access_token']
            # Expire 60 seconds early to avoid edge cases
            SpotifyClient._token_expires_at = time.time() + data['expires_in'] - 60

    def _get_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if SpotifyClient._token is None or time.time() >= SpotifyClient._token_expires_at:
            self._refresh_token()
        return SpotifyClient._token

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an authenticated request to the Spotify API."""
        url = f'{self.API_BASE_URL}{endpoint}'
        headers = {
            'Authorization': f'Bearer {self._get_token()}',
            **kwargs.pop('headers', {}),
        }

        with httpx.Client() as client:
            response = client.request(
                method,
                url,
                headers=headers,
                timeout=15.0,
                **kwargs,
            )

            # If token expired, refresh and retry once
            if response.status_code == 401:
                self._refresh_token()
                headers['Authorization'] = f'Bearer {self._get_token()}'
                response = client.request(
                    method,
                    url,
                    headers=headers,
                    timeout=15.0,
                    **kwargs,
                )

            response.raise_for_status()
            return response.json()

    def search_audiobooks(self, query: str, limit: int = 10, market: str = 'US') -> list[dict]:
        """
        Search for audiobooks on Spotify.

        Args:
            query: Search query string
            limit: Maximum number of results (default 10, max 50)
            market: Market code for availability (default 'US')

        Returns:
            List of audiobook dictionaries with title, authors, narrators, etc.
        """
        encoded_query = quote_plus(query.strip())
        endpoint = f'/search?q={encoded_query}&type=audiobook&limit={limit}&market={market}'

        data = self._make_request('GET', endpoint)
        items = data.get('audiobooks', {}).get('items', [])

        results = []
        for item in items:
            authors = [a.get('name') for a in item.get('authors', []) if a.get('name')]
            narrators = [n.get('name') for n in item.get('narrators', []) if n.get('name')]

            # Get the largest image available
            image = None
            if item.get('images'):
                image = item['images'][0].get('url')

            # Clean up description
            description = item.get('description', '') or ''

            results.append({
                'title': item.get('name', ''),
                'authors': authors,
                'narrators': narrators,
                'description': description,
                'image': image,
                'url': item.get('external_urls', {}).get('spotify'),
            })

        return results

    def get_audiobook(self, audiobook_id: str, market: str = 'US') -> dict:
        """
        Get details for a specific audiobook.

        Args:
            audiobook_id: Spotify audiobook ID
            market: Market code for availability (default 'US')

        Returns:
            Audiobook details dictionary
        """
        endpoint = f'/audiobooks/{audiobook_id}?market={market}'
        item = self._make_request('GET', endpoint)

        authors = [a.get('name') for a in item.get('authors', []) if a.get('name')]
        narrators = [n.get('name') for n in item.get('narrators', []) if n.get('name')]

        image = None
        if item.get('images'):
            image = item['images'][0].get('url')

        return {
            'title': item.get('name', ''),
            'authors': authors,
            'narrators': narrators,
            'description': item.get('description', ''),
            'image': image,
            'url': item.get('external_urls', {}).get('spotify'),
        }
