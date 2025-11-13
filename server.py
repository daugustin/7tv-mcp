"""
7TV MCP Server

An MCP server that provides tools for interacting with the 7TV emote platform.
7TV is an open-source platform for emotes and other streamer-related tools and services.
"""

from typing import Any
import httpx
from mcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("7tv-mcp")

# API Configuration
API_BASE_URL = "https://7tv.io/v3"
API_V3_BASE_URL = "https://api.7tv.app/v3"
GRAPHQL_URL = "https://7tv.io/v3/gql"
CDN_BASE_URL = "https://cdn.7tv.app"

# HTTP client for making requests
client = httpx.AsyncClient(timeout=30.0)


# Helper functions
async def make_request(url: str, method: str = "GET", json_data: dict | None = None) -> dict[str, Any]:
    """Make an HTTP request and return the JSON response."""
    try:
        if method == "POST":
            response = await client.post(url, json=json_data)
        else:
            response = await client.get(url)

        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def format_emote_result(emote: dict[str, Any]) -> str:
    """Format an emote object into a readable string."""
    emote_id = emote.get("id", "Unknown")
    name = emote.get("name", "Unknown")
    owner = emote.get("owner", {})
    owner_name = owner.get("username", "Unknown") if isinstance(owner, dict) else "Unknown"

    # Get host information
    host = emote.get("host", {})
    files = host.get("files", []) if isinstance(host, dict) else []

    # Build CDN URL (use the largest size available)
    cdn_url = "N/A"
    if files:
        # Sort by size and get the largest
        sorted_files = sorted(files, key=lambda x: int(x.get("width", 0)), reverse=True)
        if sorted_files:
            file_name = sorted_files[0].get("name", "")
            if file_name:
                cdn_url = f"{CDN_BASE_URL}/emote/{emote_id}/{file_name}"

    animated = emote.get("animated", False)
    flags = emote.get("flags", 0)

    result = f"Emote: {name}\n"
    result += f"ID: {emote_id}\n"
    result += f"Owner: {owner_name}\n"
    result += f"Animated: {animated}\n"
    result += f"URL: {cdn_url}\n"

    return result


# Tool handlers
@mcp.tool()
async def search_emotes(
    query: str,
    page: int = 1,
    limit: int = 20,
    animated: bool | None = None,
    case_sensitive: bool = False
) -> str:
    """
    Search for emotes on 7TV. This tool allows you to find emotes by name or keywords.
    You can filter by animated status and paginate through results.
    Use this when users want to find specific emotes or browse available emotes.

    Args:
        query: Search query for emotes
        page: Page number for pagination (default: 1)
        limit: Number of results per page (default: 20, max: 100)
        animated: Filter for animated emotes (true/false/null for all)
        case_sensitive: Whether the search should be case-sensitive (default: false)

    Returns:
        Formatted string with emote search results
    """
    if limit > 100:
        limit = 100

    # Build GraphQL query for searching emotes
    gql_query = """
    query SearchEmotes($query: String!, $page: Int, $limit: Int, $filter: EmoteSearchFilter) {
        emotes(query: $query, page: $page, limit: $limit, filter: $filter) {
            count
            items {
                id
                name
                owner {
                    id
                    username
                    display_name
                }
                flags
                host {
                    url
                    files {
                        name
                        format
                        width
                        height
                    }
                }
                animated
            }
        }
    }
    """

    variables = {
        "query": query,
        "page": page,
        "limit": limit,
    }

    # Add filter if animated is specified
    if animated is not None:
        variables["filter"] = {
            "animated": animated,
            "case_sensitive": case_sensitive,
        }

    result = await make_request(
        GRAPHQL_URL,
        method="POST",
        json_data={"query": gql_query, "variables": variables}
    )

    if "error" in result:
        return f"Error: {result['error']}"

    # Parse and format results
    data = result.get("data", {})
    emotes_data = data.get("emotes", {})
    items = emotes_data.get("items", [])
    count = emotes_data.get("count", 0)

    if not items:
        return f"No emotes found for query '{query}'"

    output = f"Found {count} emotes (showing page {page}, {len(items)} results):\n\n"
    for emote in items:
        output += format_emote_result(emote) + "\n"

    return output


@mcp.tool()
async def get_user_emotes(platform: str, user_id: str) -> str:
    """
    Get all emotes for a specific user on a platform (Twitch, Kick, or YouTube).
    This returns the user's active emote set including their personal emotes and any enabled emote sets.
    Use this when users want to see what emotes are available for a specific channel or user.

    Args:
        platform: Platform name (twitch, kick, youtube)
        user_id: User ID on the specified platform

    Returns:
        Formatted string with user's emotes
    """

    # Validate platform
    valid_platforms = ["twitch", "kick", "youtube"]
    if platform.lower() not in valid_platforms:
        return f"Error: Invalid platform '{platform}'. Must be one of: {', '.join(valid_platforms)}"

    url = f"{API_BASE_URL}/users/{platform.lower()}/{user_id}"
    result = await make_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    # Parse user data
    username = result.get("username", "Unknown")
    display_name = result.get("display_name", username)
    emote_set = result.get("emote_set", {})
    emotes = emote_set.get("emotes", [])

    if not emotes:
        return f"User '{display_name}' ({platform}) has no emotes"

    output = f"Emotes for {display_name} ({platform}):\n"
    output += f"Total: {len(emotes)} emotes\n\n"

    for emote in emotes:
        output += format_emote_result(emote) + "\n"

    return output


@mcp.tool()
async def get_global_emotes() -> str:
    """
    Get the global 7TV emote set that is available to all users across all platforms.
    These are universally available emotes that can be used by anyone.
    Use this to see what emotes are globally available on 7TV.

    Returns:
        Formatted string with global emotes
    """
    url = f"{API_BASE_URL}/emote-sets/global"
    result = await make_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    emotes = result.get("emotes", [])
    emote_set_name = result.get("name", "Global")

    output = f"Global 7TV Emote Set: {emote_set_name}\n"
    output += f"Total: {len(emotes)} emotes\n\n"

    for emote in emotes:
        output += format_emote_result(emote) + "\n"

    return output


@mcp.tool()
async def get_emote_details(emote_id: str) -> str:
    """
    Get detailed information about a specific emote by its ID.
    This includes the emote's name, owner, images, flags, and other metadata.
    Use this when you need comprehensive information about a particular emote.

    Args:
        emote_id: The 7TV emote ID

    Returns:
        Formatted string with emote details
    """

    # Use GraphQL to get emote details
    gql_query = """
    query GetEmote($id: ObjectID!) {
        emote(id: $id) {
            id
            name
            owner {
                id
                username
                display_name
            }
            flags
            tags
            host {
                url
                files {
                    name
                    format
                    width
                    height
                }
            }
            animated
        }
    }
    """

    result = await make_request(
        GRAPHQL_URL,
        method="POST",
        json_data={"query": gql_query, "variables": {"id": emote_id}}
    )

    if "error" in result:
        return f"Error: {result['error']}"

    data = result.get("data", {})
    emote = data.get("emote")

    if not emote:
        return f"Emote with ID '{emote_id}' not found"

    output = "Emote Details:\n\n"
    output += format_emote_result(emote)

    # Add tags if available
    tags = emote.get("tags", [])
    if tags:
        output += f"Tags: {', '.join(tags)}\n"

    return output


@mcp.tool()
async def get_emote_set(emote_set_id: str) -> str:
    """
    Get information about a specific emote set by its ID.
    An emote set is a collection of emotes that can be enabled for a channel.
    This returns all emotes in the set along with set metadata.

    Args:
        emote_set_id: The 7TV emote set ID

    Returns:
        Formatted string with emote set information
    """

    url = f"{API_V3_BASE_URL}/emote-sets/{emote_set_id}"
    result = await make_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    set_name = result.get("name", "Unknown")
    emotes = result.get("emotes", [])
    owner = result.get("owner", {})
    owner_name = owner.get("username", "Unknown") if isinstance(owner, dict) else "Unknown"

    output = f"Emote Set: {set_name}\n"
    output += f"ID: {emote_set_id}\n"
    output += f"Owner: {owner_name}\n"
    output += f"Total Emotes: {len(emotes)}\n\n"

    for emote in emotes:
        output += format_emote_result(emote) + "\n"

    return output
