"""Test MCP protocol initialization and communication."""

import pytest
import json
import subprocess
import asyncio
from pathlib import Path


@pytest.mark.asyncio
async def test_mcp_protocol_initialization(test_server_command, mcp_initialize_request):
    """Test 2: Verify MCP protocol initialization works correctly."""
    print("\n🤝 Test 2: MCP Protocol Initialization")
    print("-" * 40)
    
    try:
        # Start the MCP server as subprocess and test initialization
        process = subprocess.Popen(
            test_server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Send initialize request
        request_json = json.dumps(mcp_initialize_request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        if stdout.strip():
            try:
                response = json.loads(stdout.strip())
                
                # Verify proper JSON-RPC response
                assert response.get("jsonrpc") == "2.0", "Invalid JSON-RPC version"
                assert "result" in response, "Missing result in response"
                assert "capabilities" in response["result"], "Missing capabilities"
                assert "serverInfo" in response["result"], "Missing serverInfo"
                
                print("   ✅ MCP initialization successful")
                print(f"   ✅ Protocol version: {response['result'].get('protocolVersion')}")
                print(f"   ✅ Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
                
                capabilities = response['result']['capabilities']
                if 'tools' in capabilities:
                    print("   ✅ Tools capability enabled")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON response: {e}")
                print(f"   Raw response: {stdout}")
                assert False, f"Invalid JSON response: {e}"
        else:
            print("   ❌ No response from server")
            print(f"   STDERR: {stderr}")
            assert False, "No response from server"
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("   ❌ Server initialization timed out")
        assert False, "Server initialization timed out"
    except Exception as e:
        print(f"   ❌ Error testing MCP protocol: {e}")
        assert False, f"Error testing MCP protocol: {e}"


@pytest.mark.asyncio
async def test_mcp_response_format(test_server_command, mcp_initialize_request):
    """Test that MCP responses have correct format structure."""
    process = subprocess.Popen(
        test_server_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd()
    )
    
    try:
        request_json = json.dumps(mcp_initialize_request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        assert stdout.strip(), "No response received"
        
        response = json.loads(stdout.strip())
        
        # Verify response structure
        assert "jsonrpc" in response, "Missing jsonrpc field"
        assert "id" in response, "Missing id field"
        assert response["id"] == mcp_initialize_request["id"], "ID mismatch"
        
        result = response["result"]
        assert "protocolVersion" in result, "Missing protocolVersion"
        assert "capabilities" in result, "Missing capabilities"
        assert "serverInfo" in result, "Missing serverInfo"
        
        server_info = result["serverInfo"]
        assert "name" in server_info, "Missing server name"
        assert "version" in server_info, "Missing server version"
        
    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Server response timed out")
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON in server response")