#!/usr/bin/env python3
"""
Debug script to examine fetch_scripture tool behavior
"""

import asyncio
import json
import httpx

async def debug_fetch_scripture():
    """Debug the fetch_scripture tool to understand the correct format."""
    
    upstream_url = "https://translation-helps-mcp.pages.dev/api/mcp"
    client = httpx.AsyncClient(timeout=30.0, verify=False)
    
    print("🔍 Debugging fetch_scripture tool for John 3:16")
    print("=" * 60)
    
    try:
        # First, let's see what tools are available and their exact schemas
        print("\n1️⃣ Getting tool list and schemas...")
        tools_response = await client.get(f"{upstream_url}?method=tools/list")
        if tools_response.status_code == 200:
            tools_data = tools_response.json()
            
            # Find fetch_scripture tool
            fetch_scripture_tool = None
            for tool in tools_data.get('tools', []):
                if tool['name'] == 'fetch_scripture':
                    fetch_scripture_tool = tool
                    break
            
            if fetch_scripture_tool:
                print("✅ Found fetch_scripture tool:")
                print(f"   Name: {fetch_scripture_tool['name']}")
                print(f"   Description: {fetch_scripture_tool['description']}")
                print(f"   Input Schema: {json.dumps(fetch_scripture_tool.get('inputSchema', {}), indent=2)}")
            else:
                print("❌ fetch_scripture tool not found in tool list!")
                return
        else:
            print(f"❌ Failed to get tools: {tools_response.status_code}")
            return
        
        # Now let's try different ways to call the tool
        print("\n2️⃣ Testing different tool call methods...")
        
        # Method 1: Current proxy method (POST with tools/call)
        print("\n🧪 Method 1: POST tools/call (current proxy method)")
        try:
            response1 = await client.post(
                upstream_url,
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "fetch_scripture",
                        "arguments": {"reference": "John 3:16"}
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response1.status_code}")
            print(f"   Response: {response1.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: Direct GET with parameters
        print("\n🧪 Method 2: GET with query parameters")
        try:
            response2 = await client.get(f"{upstream_url}?method=fetch_scripture&reference=John 3:16")
            print(f"   Status: {response2.status_code}")
            print(f"   Response: {response2.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 3: POST with different structure
        print("\n🧪 Method 3: POST with tool name as method")
        try:
            response3 = await client.post(
                upstream_url,
                json={
                    "method": "fetch_scripture",
                    "params": {"reference": "John 3:16"}
                },
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response3.status_code}")
            print(f"   Response: {response3.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 4: MCP-style JSON-RPC
        print("\n🧪 Method 4: Full JSON-RPC 2.0 format")
        try:
            response4 = await client.post(
                upstream_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "fetch_scripture",
                        "arguments": {"reference": "John 3:16"}
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response4.status_code}")
            print(f"   Response: {response4.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")

        # Method 5: Try the exact URL from the error message
        print("\n🧪 Method 5: Direct API endpoint (from error message)")
        try:
            # The error showed "/api/fetch-scripture?reference=John+3%3A16"
            # Let's try the base domain with this path
            base_domain = "https://translation-helps-mcp.pages.dev"
            response5 = await client.get(f"{base_domain}/api/fetch-scripture?reference=John 3:16")
            print(f"   Status: {response5.status_code}")
            print(f"   Response: {response5.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(debug_fetch_scripture())