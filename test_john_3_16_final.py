#!/usr/bin/env python3
"""
Improved stdio test that handles MCP communication properly
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_john_3_16_stdio_improved():
    """Test John 3:16 with proper stdio handling."""
    print("📖 Testing John 3:16 via improved MCP stdio protocol")
    print("=" * 60)
    
    # Start the MCP server as subprocess
    process = subprocess.Popen(
        [sys.executable, "mcp_proxy_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd()
    )
    
    try:
        # Step 1: Initialize
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
        
        # Send initialize request
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        init_response_line = process.stdout.readline()
        if init_response_line:
            init_response = json.loads(init_response_line.strip())
            if init_response.get("jsonrpc") == "2.0" and "result" in init_response:
                print("   ✅ MCP initialization successful")
            else:
                print(f"   ❌ MCP initialization failed: {init_response}")
                return False
        else:
            print("   ❌ No initialize response received")
            return False
        
        # Step 2: Send initialized notification
        print("2️⃣ Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Give server time to process notification
        await asyncio.sleep(0.5)
        
        # Step 3: Call fetch_scripture
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
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Read tool response with timeout
        try:
            # Wait for response with asyncio timeout
            response_line = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
                timeout=10.0
            )
            
            if response_line:
                tool_response = json.loads(response_line.strip())
                
                if tool_response.get("jsonrpc") == "2.0" and "result" in tool_response:
                    result = tool_response["result"]
                    
                    # Handle MCP tool response format
                    if isinstance(result, dict) and "content" in result:
                        content_list = result["content"]
                        if isinstance(content_list, list) and len(content_list) > 0:
                            content = content_list[0]
                            if content.get("type") == "text" and content.get("text"):
                                verse_text = content["text"]
                                print("   ✅ fetch_scripture successful")
                                print(f"   📖 John 3:16: {verse_text[:100]}...")
                                
                                # Verify it's the correct verse
                                if "God so loved the world" in verse_text:
                                    print("   ✅ Correct John 3:16 text verified!")
                                    print(f"   📊 Found {verse_text.count('(')} translations")
                                    return True
                                else:
                                    print("   ⚠️  Text doesn't match expected John 3:16")
                                    return False
                            else:
                                print(f"   ❌ Unexpected content item format: {content}")
                                return False
                        else:
                            print(f"   ❌ No content in content list: {content_list}")
                            return False
                    elif isinstance(result, list) and len(result) > 0:
                        # Handle direct list format
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
            else:
                print("   ❌ No tool response received")
                return False
                
        except asyncio.TimeoutError:
            print("   ❌ Tool response timed out")
            return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    finally:
        # Clean shutdown
        try:
            process.stdin.close()
            # Give server time to clean up
            await asyncio.sleep(1.0)
            if process.poll() is None:
                process.terminate()
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(asyncio.to_thread(process.wait)),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    process.kill()
        except Exception as cleanup_error:
            print(f"   ⚠️  Cleanup warning: {cleanup_error}")

async def main():
    """Run the improved stdio test."""
    success = await test_john_3_16_stdio_improved()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: John 3:16 works via improved MCP stdio protocol!")
        print("✅ The TaskGroup error has been resolved and the server responds correctly.")
    else:
        print("❌ FAILED: Improved stdio test still has issues")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)