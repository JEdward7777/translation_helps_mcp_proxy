#!/usr/bin/env python3
"""
Proper stdio-based test for John 3:16 via MCP protocol
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_john_3_16_via_stdio():
    """Test John 3:16 via proper MCP stdio communication."""
    print("📖 Testing John 3:16 via MCP stdio protocol")
    print("=" * 60)
    
    try:
        # Start the MCP server as subprocess
        process = subprocess.Popen(
            [sys.executable, "mcp_proxy_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Step 1: Initialize the MCP connection
        print("\n1️⃣ Initializing MCP connection...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Step 2: Send initialized notification
        print("2️⃣ Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        # Step 3: Call fetch_scripture tool for John 3:16
        print("3️⃣ Calling fetch_scripture for John 3:16...")
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "fetch_scripture",
                "arguments": {
                    "reference": "John 3:16"
                }
            }
        }
        
        # Send all requests (init, initialized notification, tool call)
        requests_input = (
            json.dumps(init_request) + "\n" +
            json.dumps(initialized_notification) + "\n" +
            json.dumps(tool_request) + "\n"
        )
        
        # Get responses
        stdout, stderr = process.communicate(input=requests_input, timeout=15)
        
        if stderr.strip():
            print(f"   Server stderr: {stderr}")
        
        # Parse responses (only init response and tool response, no response for initialized notification)
        response_lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
        
        if len(response_lines) < 2:
            print(f"   ❌ Expected 2 responses, got {len(response_lines)}")
            print(f"   Raw output: {stdout}")
            return False
        
        try:
            init_response = json.loads(response_lines[0])
            # The tool response should be the second response (initialized notification doesn't get a response)
            tool_response = json.loads(response_lines[1])
        except json.JSONDecodeError as e:
            print(f"   ❌ Failed to parse JSON responses: {e}")
            print(f"   Raw responses: {response_lines}")
            return False
        
        # Check initialization
        if init_response.get("jsonrpc") == "2.0" and "result" in init_response:
            print("   ✅ MCP initialization successful")
        else:
            print(f"   ❌ MCP initialization failed: {init_response}")
            return False
        
        # Check tool response
        if tool_response.get("jsonrpc") == "2.0" and "result" in tool_response:
            result = tool_response["result"]
            if isinstance(result, list) and len(result) > 0:
                content = result[0]
                if content.get("type") == "text" and content.get("text"):
                    verse_text = content["text"]
                    print("   ✅ fetch_scripture successful")
                    print(f"   📖 John 3:16: {verse_text[:100]}...")
                    
                    # Verify it's the correct verse
                    if "God so loved the world" in verse_text:
                        print("   ✅ Correct John 3:16 text verified!")
                        return True
                    else:
                        print("   ⚠️  Text doesn't match expected John 3:16")
                        print(f"   Full text: {verse_text}")
                        return False
                else:
                    print(f"   ❌ Unexpected content format: {content}")
                    return False
            else:
                print(f"   ❌ Unexpected result format: {result}")
                return False
        else:
            print(f"   ❌ Tool call failed: {tool_response}")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("   ❌ Test timed out")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    finally:
        if process.poll() is None:
            process.terminate()

async def main():
    """Run the stdio-based John 3:16 test."""
    success = await test_john_3_16_via_stdio()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: John 3:16 works via proper MCP stdio protocol!")
        print("✅ The MCP proxy server correctly:")
        print("   - Handles MCP initialization")
        print("   - Routes fetch_scripture to the correct API endpoint")
        print("   - Returns properly formatted MCP TextContent")
        print("   - Delivers the correct John 3:16 verse text")
    else:
        print("❌ FAILED: John 3:16 stdio test failed")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)