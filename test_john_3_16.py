#!/usr/bin/env python3
"""
Focused test for John 3:16 verse fetching through the MCP proxy
"""

import asyncio
import json
from mcp_proxy_server import MCPProxyServer

async def test_john_3_16():
    """Test fetching John 3:16 through the proxy server."""
    print("📖 Testing John 3:16 verse fetching")
    print("=" * 50)
    
    proxy = MCPProxyServer(verify_ssl=False)
    
    try:
        # Test the direct _call_upstream method first
        print("\n1️⃣ Testing direct upstream call...")
        response = await proxy._call_upstream('tools/call', {
            'name': 'fetch_scripture',
            'arguments': {'reference': 'John 3:16'}
        })
        
        if response:
            print("✅ Direct upstream call successful")
            print(f"Response keys: {list(response.keys())}")
            if "scripture" in response:
                print(f"Scripture found: {len(response['scripture'])} translations")
                # Show first translation preview
                if response['scripture']:
                    first_translation = response['scripture'][0]
                    print(f"Preview: {first_translation['text'][:100]}...")
            else:
                print(f"Response: {json.dumps(response, indent=2)}")
        else:
            print("❌ Direct upstream call failed")
            return False
        
        # Test the response format directly
        print("\n2️⃣ Testing response format...")
        if "scripture" in response:
            scripture_list = response["scripture"]
            if scripture_list:
                first_scripture = scripture_list[0]
                verse_text = first_scripture.get("text", "").lower()
                
                if "god so loved the world" in verse_text:
                    print("✅ John 3:16 text verified!")
                    print(f"Full verse: {first_scripture.get('text', '')}")
                    print(f"Translation: {first_scripture.get('translation', 'Unknown')}")
                    return True
                else:
                    print("⚠️  Response doesn't contain expected John 3:16 text")
                    print(f"Actual text: {first_scripture.get('text', '')}")
                    return False
            else:
                print("❌ No scripture entries in response")
                return False
        else:
            print("❌ No 'scripture' key in response")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        await proxy.client.aclose()

async def main():
    """Run the John 3:16 test."""
    success = await test_john_3_16()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: John 3:16 can be fetched through the MCP proxy!")
        print("The fetch_scripture tool is now working correctly.")
    else:
        print("❌ FAILED: John 3:16 fetching is not working properly.")
        print("Additional debugging may be needed.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)