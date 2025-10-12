"""Test MCPO integration with the MCP proxy"""

import pytest
import asyncio
import subprocess
import time
import httpx
import json
import os
from pathlib import Path

class TestMCPOIntegration:
    """Test MCPO REST API integration"""
    
    @pytest.fixture
    def mock_api_key(self):
        """Provide a test API key"""
        return "sk-test-api-key-for-testing"
    
    @pytest.fixture
    def package_dir(self):
        """Get the package directory"""
        return Path(__file__).parent.parent / "src" / "translation_helps_mcp_proxy"
    
    def test_main_module_imports(self, package_dir):
        """Test that the main module can be imported"""
        main_path = package_dir / "__main__.py"
        assert main_path.exists(), "Main module file should exist"
        
        # Test that we can import the main module
        import sys
        sys.path.insert(0, str(package_dir.parent))
        
        try:
            import translation_helps_mcp_proxy.__main__ as main_module
            assert hasattr(main_module, 'main'), "Main function should exist"
            assert hasattr(main_module, 'create_parser'), "Parser function should exist"
        finally:
            sys.path.remove(str(package_dir.parent))
    
    def test_argument_parsing(self, package_dir):
        """Test command line argument parsing"""
        import sys
        sys.path.insert(0, str(package_dir.parent))
        
        try:
            from translation_helps_mcp_proxy.__main__ import create_parser
            
            parser = create_parser()
            
            # Test default arguments
            args = parser.parse_args([])
            assert args.upstream_url == "https://translation-helps-mcp.pages.dev/api/mcp"
            assert args.port == 8000
            assert args.with_mcpo == False
            assert args.debug == False
            
            # Test MCPO arguments
            args = parser.parse_args([
                "--with-mcpo", 
                "--port", "9000", 
                "--api-key", "test-key",
                "--debug"
            ])
            assert args.with_mcpo == True
            assert args.port == 9000
            assert args.api_key == "test-key"
            assert args.debug == True
            
        finally:
            sys.path.remove(str(package_dir.parent))
    
    def test_mcp_proxy_path_detection(self, package_dir):
        """Test that the main module can find the MCP proxy"""
        mcp_proxy_path = package_dir / "mcp_proxy_server.py"
        assert mcp_proxy_path.exists(), f"MCP proxy should exist at {mcp_proxy_path}"
    
    @pytest.mark.asyncio
    async def test_mcpo_command_building(self, package_dir, mock_api_key):
        """Test that MCPO commands are built correctly"""
        import sys
        sys.path.insert(0, str(package_dir.parent))
        
        try:
            from translation_helps_mcp_proxy.__main__ import create_parser
            
            parser = create_parser()
            args = parser.parse_args([
                "--with-mcpo",
                "--port", "8000",
                "--api-key", mock_api_key,
                "--upstream-url", "http://localhost:5173/api/mcp",
                "--enabled-tools", "fetch_scripture,fetch_translation_notes"
            ])
            
            # Verify arguments are parsed correctly
            assert args.with_mcpo == True
            assert args.port == 8000
            assert args.api_key == mock_api_key
            assert args.enabled_tools == "fetch_scripture,fetch_translation_notes"
            
        finally:
            sys.path.remove(str(package_dir.parent))
    
    def test_package_structure(self, package_dir):
        """Test that the package has the expected structure"""
        # Check required files exist
        assert (package_dir / "__init__.py").exists()
        assert (package_dir / "__main__.py").exists()
        assert (package_dir / "mcp_proxy_server.py").exists()
        
        # Check pyproject.toml exists at package root
        package_root = package_dir.parent.parent
        assert (package_root / "pyproject.toml").exists()
    
    def test_help_message(self, package_dir):
        """Test that help message is informative"""
        import sys
        sys.path.insert(0, str(package_dir.parent))
        
        try:
            from translation_helps_mcp_proxy.__main__ import create_parser
            
            parser = create_parser()
            help_text = parser.format_help()
            
            # Verify key information is in help
            assert "--with-mcpo" in help_text
            assert "--port" in help_text
            assert "--api-key" in help_text
            assert "translation-helps-mcp-proxy" in help_text
            assert "Examples:" in help_text
            
        finally:
            sys.path.remove(str(package_dir.parent))

class TestMCPOIntegrationLive:
    """Live integration tests (require network and may be slower)"""
    
    @pytest.mark.slow
    @pytest.mark.skipif(not os.getenv("TEST_MCPO_LIVE"), 
                       reason="Set TEST_MCPO_LIVE=1 to run live MCPO tests")
    @pytest.mark.asyncio
    async def test_mcpo_startup(self):
        """Test that MCPO can start up with our proxy (if MCPO is available)"""
        # This test requires MCPO to be available and is marked as slow
        # Only runs if TEST_MCPO_LIVE environment variable is set
        
        test_port = 18000  # Use unusual port to avoid conflicts
        test_api_key = "sk-test-key-integration-test"
        
        package_dir = Path(__file__).parent.parent / "src" / "translation_helps_mcp_proxy"
        main_module = package_dir / "__main__.py"
        
        # Try to start MCPO with our proxy
        cmd = [
            "python", str(main_module),
            "--with-mcpo",
            "--port", str(test_port),
            "--api-key", test_api_key,
            "--enabled-tools", "fetch_scripture"
        ]
        
        process = None
        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                pytest.fail(f"Process exited early. STDOUT: {stdout}, STDERR: {stderr}")
            
            # Try to connect to the REST API
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"http://localhost:{test_port}/docs")
                    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                    
                    # Try to access the OpenAPI schema
                    response = await client.get(f"http://localhost:{test_port}/openapi.json")
                    assert response.status_code == 200
                    
                    schema = response.json()
                    assert "openapi" in schema
                    
                except httpx.ConnectError:
                    pytest.fail(f"Could not connect to MCPO on port {test_port}")
            
        finally:
            # Clean up
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])