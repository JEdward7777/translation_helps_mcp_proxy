#!/usr/bin/env python3
"""
Main entry point for translation-helps-mcp-proxy

This script can run in two modes:
1. Standard MCP proxy mode (default)
2. MCPO REST API mode (with --with-mcpo flag)
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Translation Helps MCP Proxy Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard MCP proxy mode
  translation-helps-mcp-proxy

  # Custom upstream URL and debugging
  translation-helps-mcp-proxy --upstream-url "http://localhost:5173/api/mcp" --debug

  # List available tools
  translation-helps-mcp-proxy --list-tools
  
  # Enable only specific tools
  translation-helps-mcp-proxy --enabled-tools "fetch_scripture,fetch_translation_notes"
        """
    )
    
    # MCP proxy arguments
    parser.add_argument("--upstream-url",
                       default="https://translation-helps-mcp.pages.dev/api/mcp",
                       help="Upstream server URL (default: %(default)s)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    parser.add_argument("--enabled-tools",
                       help="Comma-separated list of enabled tools")
    parser.add_argument("--hide-params",
                       help="Comma-separated list of parameters to hide from tool schemas")
    parser.add_argument("--list-tools", action="store_true",
                       help="List available tools and exit")
    parser.add_argument("--filter-book-chapter-notes", action="store_true",
                       help="Filter out book-level and chapter-level notes from translation notes responses")
    
    return parser

def run_mcp_proxy(args):
    """Run the MCP proxy"""
    # Import here to avoid circular imports
    from .mcp_proxy_server import main as mcp_main
    
    # Convert args to sys.argv format for mcp_proxy_server
    sys.argv = ["mcp_proxy_server.py"]
    
    if args.upstream_url != "https://translation-helps-mcp.pages.dev/api/mcp":
        sys.argv.extend(["--upstream-url", args.upstream_url])
    if args.debug:
        sys.argv.append("--debug")
    if args.enabled_tools:
        sys.argv.extend(["--enabled-tools", args.enabled_tools])
    if args.hide_params:
        sys.argv.extend(["--hide-params", args.hide_params])
    if args.list_tools:
        sys.argv.append("--list-tools")
    if args.filter_book_chapter_notes:
        sys.argv.append("--filter-book-chapter-notes")
    
    # Run the MCP proxy (it's async, so we need asyncio.run)
    return asyncio.run(mcp_main())

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        return run_mcp_proxy(args)
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())