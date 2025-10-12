#!/usr/bin/env python3
"""
Debug MCPO Endpoints

Quick script to see what endpoints MCPO is actually providing
"""

import requests
import json
import sys
import time
import subprocess
from pathlib import Path

def check_mcpo_endpoints():
    port = 18080
    base_url = f"http://localhost:{port}"
    
    print(f"🔍 Checking MCPO endpoints at {base_url}")
    
    # Start MCPO server
    package_dir = Path(__file__).parent / "src" / "translation_helps_mcp_proxy"
    main_module = package_dir / "__main__.py"
    
    cmd = [
        sys.executable, str(main_module),
        "--with-mcpo",
        "--port", str(port),
        "--api-key", "sk-test-key",
        "--enabled-tools", "fetch_scripture,fetch_translation_notes"
    ]
    
    print("Starting MCPO...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Wait for startup
    time.sleep(5)
    
    try:
        # Check common endpoints
        endpoints_to_check = [
            "/",
            "/docs",
            "/openapi.json",
            "/v1/chat/completions",
            "/chat/completions",
            "/models",
            "/v1/models"
        ]
        
        for endpoint in endpoints_to_check:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=2)
                print(f"✅ {endpoint}: {response.status_code}")
                if endpoint == "/openapi.json" and response.status_code == 200:
                    try:
                        schema = response.json()
                        if "paths" in schema:
                            print(f"   Available paths: {list(schema['paths'].keys())}")
                    except:
                        pass
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        # Test a simple POST to chat completions
        try:
            chat_data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 50
            }
            
            for chat_endpoint in ["/v1/chat/completions", "/chat/completions"]:
                try:
                    response = requests.post(
                        f"{base_url}{chat_endpoint}",
                        json=chat_data,
                        headers={"Authorization": "Bearer sk-test-key"},
                        timeout=10
                    )
                    print(f"🔄 POST {chat_endpoint}: {response.status_code}")
                    if response.status_code != 404:
                        print(f"   Response: {response.text[:200]}")
                except Exception as e:
                    print(f"❌ POST {chat_endpoint}: {e}")
                    
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
        
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    check_mcpo_endpoints()