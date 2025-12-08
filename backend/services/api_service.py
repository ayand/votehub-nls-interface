"""
Service for making external API calls.
Encapsulates HTTP communication logic.
"""
import requests
from typing import Dict, Any


class ApiService:
    """Handles external API communication."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the API service.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def get(self, url: str) -> Dict[str, Any]:
        """
        Make a GET request to the specified URL.

        Args:
            url: The URL to make the request to

        Returns:
            JSON response as a dictionary

        Raises:
            requests.RequestException: If the request fails
        """
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
