"""Test complete stdio MCP workflow."""

import pytest
import json
import subprocess
import asyncio
from pathlib import Path


@pytest.mark.asyncio
async def test_stdio_workflow(test_server_command, mcp_initialize_request, 
                             mcp_initialized_notification, john_3_16_tool_request):
    """Test 4: Complete stdio MCP workflow with John 3:16."""
    print("\n📖 Test 4: Stdio MCP Workflow (John 3:16)")
    print("-" * 40)
    
    # Start the MCP server as subprocess
    process = subprocess.Popen(
        test_server_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd()
    )
    
    try:
        # Step 1: Initialize
        print("   1️⃣ Initializing MCP connection...")
        
        # Send initialize request
        process.stdin.write(json.dumps(mcp_initialize_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        init_response_line = process.stdout.readline()
        assert init_response_line, "No initialize response received"
        
        init_response = json.loads(init_response_line.strip())
        assert init_response.get("jsonrpc") == "2.0", "Invalid JSON-RPC version in init response"
        assert "result" in init_response, "Missing result in init response"
        
        print("   ✅ MCP initialization successful")
        
        # Step 2: Send initialized notification
        print("   2️⃣ Sending initialized notification...")
        
        process.stdin.write(json.dumps(mcp_initialized_notification) + "\n")
        process.stdin.flush()
        
        # Give server time to process notification
        await asyncio.sleep(0.5)
        
        # Step 3: Call fetch_scripture
        print("   3️⃣ Calling fetch_scripture for John 3:16...")
        
        process.stdin.write(json.dumps(john_3_16_tool_request) + "\n")
        process.stdin.flush()
        
        # Read tool response with timeout
        try:
            # Wait for response with asyncio timeout
            response_line = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
                timeout=10.0
            )
            
            assert response_line, "No tool response received"
            
            tool_response = json.loads(response_line.strip())
            
            assert tool_response.get("jsonrpc") == "2.0", "Invalid JSON-RPC version in tool response"
            assert "result" in tool_response, "Missing result in tool response"
            
            result = tool_response["result"]
            
            # Handle MCP tool response format
            if isinstance(result, dict) and "content" in result:
                content_list = result["content"]
                assert isinstance(content_list, list), "Content should be a list"
                assert len(content_list) > 0, "Content list should not be empty"
                
                content = content_list[0]
                assert content.get("type") == "text", "Content type should be text"
                assert content.get("text"), "Content text should not be empty"
                
                verse_text = content["text"]
                print("   ✅ fetch_scripture successful")
                print(f"   📖 John 3:16: {verse_text[:100]}...")
                
                # Verify it's the correct verse
                assert "God so loved the world" in verse_text, "Text doesn't match expected John 3:16"
                print("   ✅ Correct John 3:16 text verified!")
                print(f"   📊 Found {verse_text.count('(')} translations")
                
            elif isinstance(result, list) and len(result) > 0:
                # Handle direct list format
                content = result[0]
                assert content.get("type") == "text", "Content type should be text"
                assert content.get("text"), "Content text should not be empty"
                
                verse_text = content["text"]
                print("   ✅ fetch_scripture successful")
                print(f"   📖 John 3:16: {verse_text[:100]}...")
                
                # Verify it's the correct verse
                assert "God so loved the world" in verse_text, "Text doesn't match expected John 3:16"
                print("   ✅ Correct John 3:16 text verified!")
                
            else:
                assert False, f"Unexpected result format: {result}"
                
        except asyncio.TimeoutError:
            print("   ❌ Tool response timed out")
            assert False, "Tool response timed out"
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        assert False, f"Unexpected error: {e}"
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


@pytest.mark.asyncio
async def test_mcp_tool_call_response_format(test_server_command, mcp_initialize_request,
                                           mcp_initialized_notification, john_3_16_tool_request):
    """Test that MCP tool call responses have correct format."""
    process = subprocess.Popen(
        test_server_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd()
    )
    
    try:
        # Initialize
        process.stdin.write(json.dumps(mcp_initialize_request) + "\n")
        process.stdin.flush()
        init_response_line = process.stdout.readline()
        assert init_response_line
        
        # Send initialized notification
        process.stdin.write(json.dumps(mcp_initialized_notification) + "\n")
        process.stdin.flush()
        await asyncio.sleep(0.5)
        
        # Call tool
        process.stdin.write(json.dumps(john_3_16_tool_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=10.0
        )
        
        assert response_line, "No response received"
        
        tool_response = json.loads(response_line.strip())
        
        # Verify response structure
        assert "jsonrpc" in tool_response, "Missing jsonrpc field"
        assert "id" in tool_response, "Missing id field"
        assert tool_response["id"] == john_3_16_tool_request["id"], "ID mismatch"
        assert "result" in tool_response, "Missing result field"
        
    except asyncio.TimeoutError:
        pytest.fail("Tool call response timed out")
    finally:
        try:
            process.stdin.close()
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
        except Exception:
            pass