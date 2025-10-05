#!/usr/bin/env python3
"""
Test the actual MCP protocol communication
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_protocol():
    """Test actual MCP protocol communication."""
    print("🧪 Testing MCP Protocol Communication")
    print("=" * 50)
    
    # Create a simple MCP initialize request
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print("1. Sending initialize request to MCP server...")
    print(f"   Request: {json.dumps(initialize_request, indent=2)}")
    
    # Start the MCP server as a subprocess
    try:
        process = subprocess.Popen(
            [sys.executable, "mcp_proxy_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Send the initialize request
        request_json = json.dumps(initialize_request) + "\n"
        print(f"   Sending: {request_json.strip()}")
        
        # Write to stdin and get response
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        print(f"2. Server response:")
        print(f"   STDOUT: {stdout}")
        if stderr:
            print(f"   STDERR: {stderr}")
        
        # Try to parse the response
        if stdout.strip():
            try:
                response = json.loads(stdout.strip())
                print(f"   Parsed response: {json.dumps(response, indent=2)}")
                
                if "result" in response and "capabilities" in response["result"]:
                    print("   ✅ SUCCESS: Server returned proper initialize response!")
                    return True
                else:
                    print("   ❌ FAILED: Response missing capabilities")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ FAILED: Invalid JSON response: {e}")
                return False
        else:
            print("   ❌ FAILED: No response from server")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("   ❌ FAILED: Server timed out")
        return False
    except Exception as e:
        print(f"   ❌ FAILED: Error testing protocol: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mcp_protocol())
    if result:
        print("\n✅ MCP Protocol Test PASSED")
    else:
        print("\n❌ MCP Protocol Test FAILED")
        print("The server needs proper initialization handling")
    sys.exit(0 if result else 1)