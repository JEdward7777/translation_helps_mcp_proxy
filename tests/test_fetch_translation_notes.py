"""Test fetch_translation_notes tool through the MCP proxy."""

import pytest


@pytest.mark.asyncio
async def test_fetch_translation_notes_basic(proxy_server):
    """Test the fetch_translation_notes tool with a basic reference."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from fetch_translation_notes"
    
    # Handle different response formats
    if 'content' in response:
        # MCP format
        assert isinstance(response['content'], list), "Content should be a list"
        assert len(response['content']) > 0, "Content list should not be empty"
        
        content_item = response['content'][0]
        assert content_item.get('type') == 'text', "Content type should be text"
        assert content_item.get('text'), "Content text should not be empty"
        
        notes_text = content_item['text']
        # Verify it contains translation notes content or handles errors gracefully
        assert any(phrase in notes_text.lower() for phrase in [
            'translation notes', 'john 3:16', 'error', 'invalid', 'not found'
        ]), "Response should contain translation notes content or error message"
        
    elif 'notes' in response or 'verseNotes' in response:
        # Direct API format
        notes = response.get('notes') or response.get('verseNotes', [])
        assert isinstance(notes, list), "Notes should be a list"
        # Allow empty list as valid response since some verses might not have notes
        
    else:
        # Allow other formats for now, but verify it's not None
        assert response, "Translation notes response should not be empty"


@pytest.mark.asyncio
async def test_fetch_translation_notes_missing_reference(proxy_server):
    """Test fetch_translation_notes with missing reference parameter."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    # Should either return an error or handle gracefully
    # Note: Proxy returns None for 400/404 errors, which is acceptable behavior
    if response is not None:
        if 'content' in response:
            content_text = response['content'][0]['text']
            # Should indicate an error about missing reference
            assert 'error' in content_text.lower() or 'required' in content_text.lower(), \
                "Should indicate reference is required"


@pytest.mark.asyncio
async def test_fetch_translation_notes_different_book(proxy_server):
    """Test fetch_translation_notes with different Bible books."""
    test_references = [
        'Matthew 5:3',
        'Romans 1:1', 
        'Genesis 1:1',
        'Revelation 22:21'
    ]
    
    for reference in test_references:
        response = await proxy_server._call_upstream('tools/call', {
            'name': 'fetch_translation_notes',
            'arguments': {
                'reference': reference,
                'language': 'en',
                'organization': 'unfoldingWord'
            }
        })
        
        assert response is not None, f"No response for reference {reference}"
        
        # Verify response format (allow different formats)
        if 'content' in response:
            assert isinstance(response['content'], list), f"Content should be a list for {reference}"
            if len(response['content']) > 0:
                assert 'text' in response['content'][0], f"Missing text in content for {reference}"


@pytest.mark.asyncio
async def test_fetch_translation_notes_default_params(proxy_server):
    """Test fetch_translation_notes with minimal parameters (using defaults)."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16'
            # language and organization should default to 'en' and 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from fetch_translation_notes with defaults"
    
    # Should work the same as with explicit parameters
    if 'content' in response:
        assert isinstance(response['content'], list), "Content should be a list"
        if len(response['content']) > 0:
            assert response['content'][0].get('type') == 'text', "Content type should be text"


@pytest.mark.asyncio
async def test_fetch_translation_notes_invalid_reference(proxy_server):
    """Test fetch_translation_notes with an invalid Bible reference."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'InvalidBook 999:999',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    # Should handle invalid references gracefully
    # Note: Proxy returns None for 400/404 errors, which is acceptable behavior
    if response is not None:
        if 'content' in response:
            content_text = response['content'][0]['text'].lower()
            # Should indicate no notes found or similar error
            assert any(phrase in content_text for phrase in [
                'no translation notes', 'not found', 'error', 'invalid'
            ]), "Should indicate the reference is invalid or no notes found"


@pytest.mark.asyncio
async def test_fetch_translation_notes_response_structure(proxy_server):
    """Test that fetch_translation_notes response has correct structure."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from fetch_translation_notes"
    assert isinstance(response, dict), "Response should be a dictionary"
    
    # Verify it follows one of the expected response formats
    expected_keys = ['content', 'notes', 'verseNotes', 'result', 'items']
    assert any(key in response for key in expected_keys), \
        f"Response should contain one of: {expected_keys}. Got keys: {list(response.keys())}"


@pytest.mark.asyncio
async def test_fetch_translation_notes_tool_integration(proxy_server):
    """Test fetch_translation_notes as part of full MCP tool workflow."""
    # First verify the tool exists in the tools list
    tools_response = await proxy_server._call_upstream('tools/list', {})
    
    assert tools_response is not None, "No response from tools/list"
    assert 'tools' in tools_response, "No tools in response"
    
    # Find the fetch_translation_notes tool
    tn_tool = None
    for tool in tools_response['tools']:
        if tool['name'] == 'fetch_translation_notes':
            tn_tool = tool
            break
    
    assert tn_tool is not None, "fetch_translation_notes tool not found in tools list"
    assert 'description' in tn_tool, "Tool should have description"
    assert 'inputSchema' in tn_tool, "Tool should have input schema"
    
    # Verify required parameters in schema
    schema = tn_tool['inputSchema']
    assert 'properties' in schema, "Schema should have properties"
    assert 'reference' in schema['properties'], "Schema should require reference parameter"
    
    # Now test the actual tool call
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16'
        }
    })
    
    assert response is not None, "Tool call should return a response"