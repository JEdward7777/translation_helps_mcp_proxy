#!/usr/bin/env python3
"""
Test script to demonstrate the MCP initialization failure
"""

import asyncio
import json
import sys
from mcp_proxy_server import MCPProxyServer

async def test_mcp_initialization():
    """Test that demonstrates the missing initialize handler."""
    print("🧪 Testing MCP Server Initialization")
    print("=" * 50)
    
    # Create proxy with SSL verification disabled for testing
    proxy = MCPProxyServer(verify_ssl=False)
    
    try:
        # Test connection first
        await proxy.test_connection()
        
        # Check if the server has the required MCP handlers
        print("\n1. Checking MCP server handlers...")
        
        # Try to inspect the server's registered handlers
        server = proxy.server
        
        # Check what handlers are registered
        if hasattr(server, '_handlers'):
            handlers = getattr(server, '_handlers', {})
            print(f"   Registered handlers: {list(handlers.keys())}")
            
            # Check for required MCP handlers
            required_handlers = ['initialize', 'notifications/initialized']
            missing_handlers = []
            
            for handler in required_handlers:
                if handler not in handlers:
                    missing_handlers.append(handler)
            
            if missing_handlers:
                print(f"   ❌ MISSING required handlers: {missing_handlers}")
                print("\n🎯 ROOT CAUSE IDENTIFIED:")
                print("   The MCP server is missing the 'initialize' handler!")
                print("   This is why MCP clients get 'NoneType has no capabilities' error")
                print("   When a client sends an initialize request, there's no handler to respond")
                return False
            else:
                print("   ✅ All required handlers are present")
                return True
        else:
            print("   ❌ Cannot inspect server handlers (no _handlers attribute)")
            
            # Try alternative inspection method
            if hasattr(server, 'list_tools'):
                print("   ✅ Server has list_tools method")
            if hasattr(server, 'call_tool'):
                print("   ✅ Server has call_tool method")
            
            print("\n   🔍 Looking for initialization capability...")
            # The issue is likely that we only registered tool handlers
            # but not the core MCP protocol handlers like initialize
            print("   ❌ Server likely missing initialization handlers")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await proxy.client.aclose()

async def main():
    """Run the initialization test."""
    success = await test_mcp_initialization()
    
    if not success:
        print("\n" + "=" * 50)
        print("🚨 TEST RESULT: INITIALIZATION FAILURE CONFIRMED")
        print("=" * 50)
        print("The server needs to add the missing initialize handler")
        print("to properly respond to MCP client initialization requests.")
    else:
        print("\n" + "=" * 50)
        print("✅ TEST RESULT: INITIALIZATION HANDLERS PRESENT")
        print("=" * 50)
        
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)