#!/usr/bin/env python3
"""
7TV MCP Server - CLI Testing Tool

A command-line interface for testing the 7TV MCP server tools directly
without needing to set up the full MCP infrastructure.
"""

import asyncio
import argparse
import sys
from typing import Any


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="7TV MCP Server CLI - Test tools locally",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for emotes
  python cli.py search "Pog" --limit 5

  # Get user emotes
  python cli.py user-emotes twitch 70647828

  # Get global emotes
  python cli.py global-emotes

  # Get emote details
  python cli.py emote-details 603caa69fccf9c40e807ab87

  # Get emote set
  python cli.py emote-set 62cdd34e72a832540de95857

  # Copy emotes between sets (requires auth)
  python cli.py copy-emotes SOURCE_SET_ID TARGET_SET_ID --token YOUR_JWT_TOKEN --override
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    subparsers.required = True

    # Search emotes command
    search_parser = subparsers.add_parser("search", help="Search for emotes")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    search_parser.add_argument("--limit", type=int, default=20, help="Results per page (default: 20, max: 100)")
    search_parser.add_argument("--animated", type=str, choices=["true", "false"], help="Filter by animated status")
    search_parser.add_argument("--case-sensitive", action="store_true", help="Case-sensitive search")

    # Get user emotes command
    user_parser = subparsers.add_parser("user-emotes", help="Get user's emotes")
    user_parser.add_argument("platform", choices=["twitch", "kick", "youtube"], help="Platform name")
    user_parser.add_argument("user_id", help="User ID on the platform")

    # Get global emotes command
    subparsers.add_parser("global-emotes", help="Get global 7TV emotes")

    # Get emote details command
    emote_parser = subparsers.add_parser("emote-details", help="Get emote details")
    emote_parser.add_argument("emote_id", help="7TV emote ID")

    # Get emote set command
    set_parser = subparsers.add_parser("emote-set", help="Get emote set details")
    set_parser.add_argument("emote_set_id", help="7TV emote set ID")

    # Copy emotes command
    copy_parser = subparsers.add_parser("copy-emotes", help="Copy emotes between sets (requires auth)")
    copy_parser.add_argument("source_set_id", help="Source emote set ID")
    copy_parser.add_argument("target_set_id", help="Target emote set ID")
    copy_parser.add_argument("--token", required=True, help="JWT Bearer token for authentication")
    copy_parser.add_argument("--override", action="store_true", help="Override conflicting emotes")

    return parser


async def run_command(args: argparse.Namespace) -> str:
    """Execute the specified command with the provided arguments."""

    # Import the tool functions here to avoid import errors when just showing help
    from server import (
        search_emotes,
        get_user_emotes,
        get_global_emotes,
        get_emote_details,
        get_emote_set,
        copy_emotes_between_sets,
    )

    if args.command == "search":
        animated = None
        if args.animated:
            animated = args.animated.lower() == "true"

        return await search_emotes(
            query=args.query,
            page=args.page,
            limit=args.limit,
            animated=animated,
            case_sensitive=args.case_sensitive
        )

    elif args.command == "user-emotes":
        return await get_user_emotes(
            platform=args.platform,
            user_id=args.user_id
        )

    elif args.command == "global-emotes":
        return await get_global_emotes()

    elif args.command == "emote-details":
        return await get_emote_details(emote_id=args.emote_id)

    elif args.command == "emote-set":
        return await get_emote_set(emote_set_id=args.emote_set_id)

    elif args.command == "copy-emotes":
        return await copy_emotes_between_sets(
            source_set_id=args.source_set_id,
            target_set_id=args.target_set_id,
            auth_token=args.token,
            override_conflicts=args.override
        )

    else:
        return f"Unknown command: {args.command}"


async def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        result = await run_command(args)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cli_entry() -> None:
    """Entry point for the CLI when run as a script."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    cli_entry()
