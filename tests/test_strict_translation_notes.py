"""Strict test for fetch_translation_notes that expects actual content, not errors."""

import pytest
import json
import subprocess
import asyncio
from pathlib import Path


@pytest.mark.asyncio
async def test_fetch_translation_notes_expects_content(test_server_command, mcp_initialize_request, mcp_initialized_notification):
    """Test that expects actual translation notes content through full MCP workflow."""
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
        # Initialize MCP connection
        process.stdin.write(json.dumps(mcp_initialize_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        init_response_line = process.stdout.readline()
        assert init_response_line, "No initialize response"
        
        # Send initialized notification
        process.stdin.write(json.dumps(mcp_initialized_notification) + "\n")
        process.stdin.flush()
        await asyncio.sleep(0.5)
        
        # Call fetch_translation_notes tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "fetch_translation_notes",
                "arguments": {
                    "reference": "John 3:16"
                }
            }
        }
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Read tool response
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=10.0
        )
        
        assert response_line, "No tool response received"
        tool_response = json.loads(response_line.strip())
        
        # Verify proper MCP response structure
        assert tool_response.get("jsonrpc") == "2.0", "Invalid JSON-RPC version"
        assert "result" in tool_response, "Missing result in response"
        
        # For MCP tool calls, result can be either direct list or wrapped in content
        result = tool_response["result"]
        
        if isinstance(result, dict) and "content" in result:
            # Wrapped format: {"content": [...], "isError": false}
            content_list = result["content"]
            assert isinstance(content_list, list), "Content should be a list"
            assert len(content_list) > 0, "Content should not be empty"
            content_item = content_list[0]
        else:
            # Direct list format: [{"type": "text", "text": "..."}]
            assert isinstance(result, list), "Result should be a list"
            assert len(result) > 0, "Result should not be empty"
            content_item = result[0]
        
        assert content_item.get("type") == "text", "Content type should be text"
        assert content_item.get("text"), "Content text should not be empty"
        
        notes_text = content_item["text"]
        
        # This should PASS only if we get actual translation notes content
        assert any(phrase in notes_text.lower() for phrase in [
            'translation notes', 'john 3:16', 'verse', 'commentary', 'introduction'
        ]), f"Should contain actual translation notes content, got: {notes_text[:200]}..."
        
        # Should be substantial content
        assert len(notes_text) > 100, "Translation notes should be substantial content"
        
        print(f"✅ Translation notes test passed - got {len(notes_text)} characters of content")
        
    except asyncio.TimeoutError:
        pytest.fail("Tool response timed out")
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


@pytest.mark.asyncio  
async def test_get_translation_word_expects_content(test_server_command, mcp_initialize_request, mcp_initialized_notification):
    """Test that expects actual translation word content through full MCP workflow."""
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
        # Initialize MCP connection
        process.stdin.write(json.dumps(mcp_initialize_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        init_response_line = process.stdout.readline()
        assert init_response_line, "No initialize response"
        
        # Send initialized notification
        process.stdin.write(json.dumps(mcp_initialized_notification) + "\n")
        process.stdin.flush()
        await asyncio.sleep(0.5)
        
        # Call get_translation_word tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_translation_word",
                "arguments": {
                    "reference": "John 3:16"
                }
            }
        }
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Read tool response
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=10.0
        )
        
        assert response_line, "No tool response received"
        tool_response = json.loads(response_line.strip())
        
        # Verify proper MCP response structure
        assert tool_response.get("jsonrpc") == "2.0", "Invalid JSON-RPC version"
        assert "result" in tool_response, "Missing result in response"
        
        # For MCP tool calls, result can be either direct list or wrapped in content
        result = tool_response["result"]
        
        if isinstance(result, dict) and "content" in result:
            # Wrapped format: {"content": [...], "isError": false}
            content_list = result["content"]
            assert isinstance(content_list, list), "Content should be a list"
            assert len(content_list) > 0, "Content should not be empty"
            content_item = content_list[0]
        else:
            # Direct list format: [{"type": "text", "text": "..."}]
            assert isinstance(result, list), "Result should be a list"
            assert len(result) > 0, "Result should not be empty"
            content_item = result[0]
        
        assert content_item.get("type") == "text", "Content type should be text"
        assert content_item.get("text"), "Content text should not be empty"
        
        words_text = content_item["text"]
        
        # This should PASS only if we get actual translation word content
        assert any(phrase in words_text.lower() for phrase in [
            'translation notes', 'god', 'love', 'faith', 'word', 'definition'
        ]), f"Should contain actual translation word content, got: {words_text[:200]}..."
        
        # Should be substantial content
        assert len(words_text) > 50, "Translation words should be substantial content"
        
        print(f"✅ Translation words test passed - got {len(words_text)} characters of content")
        
    except asyncio.TimeoutError:
        pytest.fail("Tool response timed out")
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