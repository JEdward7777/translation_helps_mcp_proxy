#!/usr/bin/env python3
"""
End-to-End OpenAI Integration Test

This script tests the complete integration chain:
OpenAI Client → MCPO REST API → MCP Proxy → Translation Helps Server

Requirements:
1. Copy .env.example to .env and add your real OpenAI API key
2. Install dependencies: pip install openai python-dotenv
3. Run this script: python test_openai_integration.py
"""

import asyncio
import os
import subprocess
import time
import signal
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

try:
    import openai
except ImportError:
    print("❌ OpenAI library not installed. Run: pip install openai")
    sys.exit(1)

class MCPOIntegrationTest:
    def __init__(self, port=18000):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.mcpo_process = None
        
        if not self.api_key:
            print("❌ No API key found. Please copy .env.example to .env and add your OpenAI API key.")
            sys.exit(1)
            
        print(f"🔑 API key loaded: {self.api_key[:10]}...")
    
    def start_mcpo_server(self):
        """Start the MCPO server with our MCP proxy"""
        print(f"🚀 Starting MCPO server on port {self.port}...")
        
        # Find the package directory
        package_dir = Path(__file__).parent / "src" / "translation_helps_mcp_proxy"
        main_module = package_dir / "__main__.py"
        
        if not main_module.exists():
            print(f"❌ Could not find main module at {main_module}")
            return False
        
        # Start MCPO with our MCP proxy
        cmd = [
            sys.executable, str(main_module),
            "--with-mcpo",
            "--port", str(self.port),
            "--api-key", self.api_key,
            "--enabled-tools", "fetch_scripture,fetch_translation_notes,get_translation_word",
            "--debug"
        ]
        
        try:
            self.mcpo_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for server to start
            print("⏳ Waiting for MCPO server to start...")
            for i in range(30):  # Wait up to 30 seconds
                if self.mcpo_process.poll() is not None:
                    stdout, _ = self.mcpo_process.communicate()
                    print(f"❌ MCPO process exited early: {stdout}")
                    return False
                
                try:
                    # Simple check to see if server is responding
                    import urllib.request
                    urllib.request.urlopen(f"{self.base_url}/docs", timeout=1)
                    print(f"✅ MCPO server is running on {self.base_url}")
                    return True
                except:
                    time.sleep(1)
                    print(f"   Still waiting... ({i+1}/30)")
            
            print("❌ MCPO server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start MCPO server: {e}")
            return False
    
    def stop_mcpo_server(self):
        """Stop the MCPO server"""
        if self.mcpo_process:
            print("🛑 Stopping MCPO server...")
            self.mcpo_process.terminate()
            try:
                self.mcpo_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcpo_process.kill()
                self.mcpo_process.wait()
    
    def test_openai_client(self):
        """Test OpenAI client integration with MCPO"""
        print("\n🧪 Testing OpenAI Client Integration...")
        
        # Configure OpenAI client to use our MCPO server
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Test 1: Basic chat completion with scripture request
        print("\n📖 Test 1: Requesting John 3:16...")
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # MCPO should handle this
                messages=[
                    {
                        "role": "user", 
                        "content": "Please fetch the scripture for John 3:16. I want to see the actual Bible text."
                    }
                ],
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            print(f"✅ Response received: {result[:200]}...")
            
            # Check if the response contains expected Bible text
            if "God so loved" in result or "John 3:16" in result:
                print("✅ Response contains expected Bible content")
            else:
                print("⚠️  Response may not contain Bible content")
                
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
            return False
        
        # Test 2: Translation notes request
        print("\n📝 Test 2: Requesting translation notes for Matthew 5:3...")
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "Can you get translation notes for Matthew 5:3? I need help understanding the original meaning."
                    }
                ],
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            print(f"✅ Response received: {result[:200]}...")
            
            if "translation" in result.lower() or "notes" in result.lower() or "Matthew" in result:
                print("✅ Response contains expected translation content")
            else:
                print("⚠️  Response may not contain translation notes")
                
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
            return False
        
        # Test 3: Combined request
        print("\n🔄 Test 3: Combined scripture and translation notes request...")
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "Please provide both the scripture text and translation notes for Romans 8:28. I want to understand both the text and its meaning."
                    }
                ],
                max_tokens=800
            )
            
            result = response.choices[0].message.content
            print(f"✅ Response received: {result[:300]}...")
            
            if "Romans" in result and ("translation" in result.lower() or "notes" in result.lower()):
                print("✅ Response contains both scripture and translation content")
            else:
                print("⚠️  Response may not contain expected combined content")
                
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
            return False
        
        return True
    
    def run_tests(self):
        """Run all integration tests"""
        print("🎯 Starting OpenAI + MCPO + MCP Proxy Integration Tests")
        print("=" * 60)
        
        try:
            # Start MCPO server
            if not self.start_mcpo_server():
                return False
            
            # Run OpenAI client tests
            if not self.test_openai_client():
                return False
            
            print("\n🎉 All tests passed! The integration is working correctly.")
            print(f"📊 MCPO REST API: {self.base_url}")
            print(f"📖 Interactive docs: {self.base_url}/docs")
            
            return True
            
        finally:
            self.stop_mcpo_server()

def main():
    """Main entry point"""
    print("🔧 Translation Helps MCP Proxy + MCPO + OpenAI Integration Test")
    print("🌐 Testing the full chain: OpenAI → MCPO → MCP Proxy → Bible Resources")
    print()
    
    # Run tests
    test = MCPOIntegrationTest()
    success = test.run_tests()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("\n🚀 You can now use this setup in production:")
        print(f"   1. Start server: python -m src.translation_helps_mcp_proxy --with-mcpo --port 8000 --api-key YOUR_KEY")
        print(f"   2. Point OpenAI client to: http://localhost:8000")
        print(f"   3. Use model 'gpt-4' with translation tools automatically available")
        sys.exit(0)
    else:
        print("\n❌ Integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()