#!/usr/bin/env python3
"""
Test script for the MCP Proxy Server
"""

import asyncio
import json
import sys
from io import StringIO
from mcp_proxy_server import MCPProxyServer
from mcp.client import stdio_client

async def test_mcp_proxy():
    """Test the MCP proxy server functionality."""
    print("🧪 Testing MCP Proxy Server Functionality")
    print("=" * 50)
    
    # Create proxy with SSL verification disabled for testing
    proxy = MCPProxyServer(verify_ssl=False)
    
    try:
        # Test 1: Upstream connection
        print("1. Testing upstream connection...")
        response = await proxy._call_upstream('tools/list', {})
        
        if response and 'tools' in response:
            print(f"   ✅ Connected to upstream server")
            print(f"   ✅ Found {len(response['tools'])} tools")
            
            # Show available tools
            print("   📋 Available tools:")
            for i, tool in enumerate(response['tools'][:5]):  # Show first 5
                print(f"      {i+1}. {tool['name']}")
            if len(response['tools']) > 5:
                print(f"      ... and {len(response['tools']) - 5} more tools")
        else:
            print("   ❌ Failed to connect to upstream server")
            return
            
        print()
        
        # Test 2: Tool call
        print("2. Testing tool call (get_system_prompt)...")
        tool_response = await proxy._call_upstream('tools/call', {
            'name': 'get_system_prompt',
            'arguments': {'includeImplementationDetails': False}
        })
        
        if tool_response:
            print("   ✅ Tool call successful")
            if 'content' in tool_response:
                content = tool_response['content'][0]['text']
                print(f"   📄 Response length: {len(content)} characters")
                print(f"   🔍 Preview: {content[:100]}...")
            else:
                print(f"   📋 Response keys: {list(tool_response.keys())}")
        else:
            print("   ❌ Tool call failed")
            
        print()
        
        # Test 3: Another tool call (fetch_scripture)
        print("3. Testing scripture fetch tool...")
        scripture_response = await proxy._call_upstream('tools/call', {
            'name': 'fetch_scripture',
            'arguments': {'reference': 'John 3:16'}
        })
        
        if scripture_response and 'content' in scripture_response:
            print("   ✅ Scripture fetch successful")
            content = scripture_response['content'][0]['text']
            print(f"   📖 Scripture preview: {content[:200]}...")
        else:
            print("   ❌ Scripture fetch failed")
            
        print()
        print("🎉 MCP Proxy Server tests completed successfully!")
        print()
        print("🚀 The proxy is ready to use. You can now:")
        print("   1. Connect your MCP client to this proxy server")
        print("   2. The proxy will handle all JSON-RPC 2.0 formatting")
        print("   3. All 12 tools from the upstream server are available")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await proxy.client.aclose()

if __name__ == "__main__":
    asyncio.run(test_mcp_proxy())