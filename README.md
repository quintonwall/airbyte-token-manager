# airbyte-token-manager

A singleton that manages fetching and refreshing Airbyte access tokens for API authentication.

## Overview

This module provides a thread-safe singleton token manager that handles Airbyte API access token creation, caching, and automatic refresh without relying on environment variables. All credentials must be passed explicitly during configuration.

## Features

- **Singleton Pattern**: Ensures only one token manager instance exists across your application
- **Thread-Safe**: Safe to use in multi-threaded applications
- **Automatic Token Refresh**: Handles token expiration and refresh automatically
- **Multiple Endpoint Support**: Tries multiple Airbyte API endpoints for maximum compatibility
- **No Environment Dependencies**: All credentials passed explicitly (no env vars required)
- **Token Caching**: Reuses valid tokens to minimize API calls

## Installation

Simply copy `token_manager.py` to your project directory.

## Quick Start

```python
from token_manager import get_token_manager

# Get the singleton instance
token_manager = get_token_manager()

# Configure with your Airbyte credentials
token_manager.configure(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    workspace_id="your_workspace_id"
)

# Get a valid access token
token = token_manager.get_token()

# Or get the authorization header directly
auth_header = token_manager.get_auth_header()
# Returns: {"Authorization": "Bearer your_access_token"}
```

## Detailed Usage

### Configuration

```python
from token_manager import TokenManager, get_token_manager

# Method 1: Using convenience function (recommended)
manager = get_token_manager()

# Method 2: Direct instantiation (also returns singleton)
manager = TokenManager()

# Configure the manager
manager.configure(
    client_id="your_airbyte_client_id",
    client_secret="your_airbyte_client_secret",
    workspace_id="your_airbyte_workspace_id"
)

# Check if configured
if manager.is_configured():
    print("Token manager is ready to use")
```

### Getting Tokens

```python
# Get access token (creates new token if needed)
token = manager.get_token()

# Get authorization header for API requests
headers = manager.get_auth_header()

# Use with requests
import requests
response = requests.get(
    "https://api.airbyte.com/v1/workspaces",
    headers=headers
)
```

### Token Management

```python
# Get token information
info = manager.get_token_info()
print(f"Has token: {info['has_token']}")
print(f"Token type: {info['token_type']}")
print(f"Expires at: {info['expires_at']}")
print(f"Is valid: {info['is_valid']}")

# Force token refresh (invalidate current token)
manager.invalidate_token()

# Next call to get_token() will create a new token
new_token = manager.get_token()
```

### Error Handling

```python
try:
    # Configure the manager
    manager.configure(client_id, client_secret, workspace_id)
    
    # Get token
    token = manager.get_token()
    
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Token creation failed: {e}")
```

## Integration Example

```python
import requests
from token_manager import get_token_manager

class AirbyteClient:
    def __init__(self, client_id: str, client_secret: str, workspace_id: str):
        self.token_manager = get_token_manager()
        self.token_manager.configure(client_id, client_secret, workspace_id)
        self.base_url = "https://api.airbyte.com/v1"
    
    def make_request(self, endpoint: str, method: str = "GET", **kwargs):
        """Make authenticated request to Airbyte API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.token_manager.get_auth_header()
        
        # Merge with any additional headers
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        response = requests.request(method, url, **kwargs)
        
        # Handle token expiration
        if response.status_code == 401:
            self.token_manager.invalidate_token()
            # Retry with new token
            headers = self.token_manager.get_auth_header()
            kwargs['headers'].update(headers)
            response = requests.request(method, url, **kwargs)
        
        return response
    
    def list_workspaces(self):
        """List all workspaces."""
        return self.make_request("/workspaces")
    
    def get_connections(self):
        """Get all connections in the workspace."""
        return self.make_request("/connections")

# Usage
client = AirbyteClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    workspace_id="your_workspace_id"
)

workspaces = client.list_workspaces()
connections = client.get_connections()
```

## API Reference

### TokenManager Class

#### Methods

- `configure(client_id, client_secret, workspace_id)`: Configure the token manager with credentials
- `is_configured()`: Check if the manager has been configured
- `get_token()`: Get a valid access token (creates/refreshes as needed)
- `get_auth_header()`: Get authorization header dictionary
- `invalidate_token()`: Force token refresh on next use
- `get_token_info()`: Get current token status information

#### Properties

All internal properties are private. Use the public methods to interact with the token manager.

### Convenience Functions

- `get_token_manager()`: Returns the singleton TokenManager instance

## Thread Safety

The TokenManager is thread-safe and can be safely used in multi-threaded applications. All token operations are protected by locks to prevent race conditions.

## Requirements

- Python 3.6+
- `requests` library

## License

This project is open source. See the repository for license details.
