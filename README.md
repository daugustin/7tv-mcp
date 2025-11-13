# 7TV MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with the [7TV emote platform](https://7tv.app/). 7TV is an open-source platform for emotes and other streamer-related tools and services.

## Features

This MCP server provides the following tools:

### 1. **search_emotes**
Search for emotes on 7TV by name or keywords. Supports filtering and pagination.

**Parameters:**
- `query` (required): Search query for emotes
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of results per page (default: 20, max: 100)
- `animated` (optional): Filter for animated emotes (true/false/null for all)
- `case_sensitive` (optional): Whether the search should be case-sensitive (default: false)

**Example:**
```json
{
  "query": "Pog",
  "page": 1,
  "limit": 10,
  "animated": true
}
```

### 2. **get_user_emotes**
Get all emotes for a specific user on a platform (Twitch, Kick, or YouTube).

**Parameters:**
- `platform` (required): Platform name (twitch, kick, or youtube)
- `user_id` (required): User ID on the specified platform

**Example:**
```json
{
  "platform": "twitch",
  "user_id": "70647828"
}
```

### 3. **get_global_emotes**
Get the global 7TV emote set that is available to all users across all platforms.

**Parameters:** None

### 4. **get_emote_details**
Get detailed information about a specific emote by its ID.

**Parameters:**
- `emote_id` (required): The 7TV emote ID

**Example:**
```json
{
  "emote_id": "603caa69fccf9c40e807ab87"
}
```

### 5. **get_emote_set**
Get information about a specific emote set by its ID.

**Parameters:**
- `emote_set_id` (required): The 7TV emote set ID

**Example:**
```json
{
  "emote_set_id": "62cdd34e72a832540de95857"
}
```

### 6. **copy_emotes_between_sets** ⚠️ Requires Authentication
Copy all emotes from one emote set to another. This is an authenticated operation requiring a valid 7TV JWT token.

**Parameters:**
- `source_set_id` (required): The 7TV emote set ID to copy from
- `target_set_id` (required): The 7TV emote set ID to copy to
- `auth_token` (required): JWT Bearer token for authentication
- `override_conflicts` (optional): Whether to override existing emotes with the same name (default: false)

**Example:**
```json
{
  "source_set_id": "62cdd34e72a832540de95857",
  "target_set_id": "65a1b2c3d4e5f6789abcdef0",
  "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "override_conflicts": false
}
```

**Use cases:**
- Copy emotes from one channel to another
- Backup emote sets by copying to a personal set
- Merge emote collections
- Clone emote set configurations

## Authentication

Some tools (like `copy_emotes_between_sets`) require authentication with a 7TV JWT token. Here's how to obtain your token:

### Getting Your 7TV Token

1. **Login to 7TV**: Visit [7tv.app](https://7tv.app) and log in with your account
2. **Open Browser DevTools**: Press `F12` or right-click and select "Inspect"
3. **Open Console**: Navigate to the "Console" tab
4. **Get Token**: Run this command:
   ```javascript
   localStorage.getItem('7tv-token')
   ```
5. **Copy Token**: Copy the token value (without quotes)

### Token Security

⚠️ **Important Security Notes:**
- Your JWT token is sensitive information that grants access to your 7TV account
- Never share your token publicly or commit it to version control
- Tokens may expire and need to be refreshed
- If you suspect your token has been compromised, log out of 7TV and log back in to invalidate the old token

### Authentication Headers

When authenticated operations are performed, the server sends requests with:
```http
Authorization: Bearer <your-jwt-token>
```

The 7TV API validates the token and checks if you have permission to perform the requested operation (e.g., modifying emote sets).

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

1. Clone this repository or download the files
2. Install dependencies:

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

### Running the Server

The server can be run directly:

```bash
python server.py
```

### Configuring with Claude Desktop

Add this to your Claude Desktop configuration file:

**MacOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "7tv": {
      "command": "python",
      "args": ["/path/to/7tv-mcp/server.py"]
    }
  }
}
```

Or if using uv:

```json
{
  "mcpServers": {
    "7tv": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/7tv-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

## API Information

This MCP server uses the 7TV API v3:

- **REST API Base:** https://7tv.io/v3
- **GraphQL Endpoint:** https://7tv.io/v3/gql
- **CDN:** https://cdn.7tv.app

### API Endpoints Used

- Global emotes: `GET https://7tv.io/v3/emote-sets/global`
- User emotes: `GET https://7tv.io/v3/users/{platform}/{user_id}`
- Emote sets: `GET https://api.7tv.app/v3/emote-sets/{emote_set_id}`
- Search (GraphQL): `POST https://7tv.io/v3/gql`

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy server.py
```

### Linting

```bash
ruff check .
```

## Design Philosophy

This MCP server follows MCP best practices:

1. **Workflow-Oriented**: Tools are designed around complete workflows (searching, browsing user emotes) rather than raw API endpoints
2. **Optimized for Context**: Returns high-signal information formatted for LLM consumption
3. **Clear Error Messages**: Provides actionable error messages with specific guidance
4. **Comprehensive Documentation**: Each tool has detailed descriptions and parameter schemas

## Use Cases

- **Browse Emotes**: Search and discover emotes across the 7TV platform
- **Channel Management**: View what emotes are available for specific channels
- **Emote Research**: Get detailed information about specific emotes or emote sets
- **Integration**: Build chatbots or tools that work with 7TV emotes

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

## Resources

- [7TV Website](https://7tv.app/)
- [7TV GitHub](https://github.com/SevenTV)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Acknowledgments

- 7TV team for providing the API
- Anthropic for the Model Context Protocol specification
