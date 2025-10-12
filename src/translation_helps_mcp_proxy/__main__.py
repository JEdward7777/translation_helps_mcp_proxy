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
        description="Translation Helps MCP Proxy Server with optional MCPO REST API integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard MCP proxy mode
  translation-helps-mcp-proxy

  # With MCPO REST API integration
  translation-helps-mcp-proxy --with-mcpo --port 8000 --api-key "your-openai-key"

  # Custom upstream URL and debugging
  translation-helps-mcp-proxy --upstream-url "http://localhost:5173/api/mcp" --debug

  # List available tools
  translation-helps-mcp-proxy --list-tools
        """
    )
    
    # Original MCP proxy arguments
    parser.add_argument("--upstream-url", 
                       default="https://translation-helps-mcp.pages.dev/api/mcp",
                       help="Upstream server URL (default: %(default)s)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    parser.add_argument("--enabled-tools", 
                       help="Comma-separated list of enabled tools")
    parser.add_argument("--list-tools", action="store_true",
                       help="List available tools and exit")
    
    # MCPO integration arguments
    parser.add_argument("--with-mcpo", action="store_true",
                       help="Enable MCPO REST API integration")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for MCPO REST API (default: %(default)s)")
    parser.add_argument("--api-key", 
                       help="API key for MCPO (can also use OPENAI_API_KEY env var)")
    
    return parser

def run_mcp_proxy(args):
    """Run the standard MCP proxy"""
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
    if args.list_tools:
        sys.argv.append("--list-tools")
    
    # Run the original MCP proxy (it's async, so we need asyncio.run)
    return asyncio.run(mcp_main())

def run_with_mcpo(args):
    """Run MCPO with the MCP proxy as backend"""
    try:
        import subprocess
        import tempfile
        import json
        
        # Get API key from args or environment
        api_key = args.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: API key required for MCPO mode. Use --api-key or set OPENAI_API_KEY environment variable.")
            return 1
        
        # Find the mcp_proxy_server.py in our package
        package_dir = Path(__file__).parent
        mcp_proxy_path = package_dir / "mcp_proxy_server.py"
        
        if not mcp_proxy_path.exists():
            print(f"Error: Could not find mcp_proxy_server.py at {mcp_proxy_path}")
            return 1
        
        # Build the MCP proxy command
        mcp_cmd = [sys.executable, str(mcp_proxy_path)]
        
        if args.upstream_url != "https://translation-helps-mcp.pages.dev/api/mcp":
            mcp_cmd.extend(["--upstream-url", args.upstream_url])
        if args.debug:
            mcp_cmd.append("--debug")
        if args.enabled_tools:
            mcp_cmd.extend(["--enabled-tools", args.enabled_tools])
        
        # Build the MCPO command
        mcpo_cmd = [
            "uvx", "mcpo",
            "--port", str(args.port),
            "--api-key", api_key,
            "--"
        ] + mcp_cmd
        
        print(f"Starting MCPO REST API on port {args.port}...")
        print(f"MCP proxy backend: {' '.join(mcp_cmd)}")
        print(f"REST API will be available at: http://localhost:{args.port}")
        print(f"API docs available at: http://localhost:{args.port}/docs")
        print()
        
        # Run MCPO
        result = subprocess.run(mcpo_cmd)
        return result.returncode
        
    except ImportError as e:
        print(f"Error: MCPO dependencies not available: {e}")
        print("Try: pip install mcpo")
        return 1
    except Exception as e:
        print(f"Error running MCPO: {e}")
        return 1

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.with_mcpo:
            return run_with_mcpo(args)
        else:
            return run_mcp_proxy(args)
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())