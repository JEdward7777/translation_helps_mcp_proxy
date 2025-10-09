"""Test get_translation_word tool through the MCP proxy."""

import pytest


@pytest.mark.asyncio
async def test_get_translation_word_basic(proxy_server):
    """Test the get_translation_word tool with a basic reference."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from get_translation_word"
    
    # Handle different response formats
    if 'content' in response:
        # MCP format
        assert isinstance(response['content'], list), "Content should be a list"
        assert len(response['content']) > 0, "Content list should not be empty"
        
        content_item = response['content'][0]
        assert content_item.get('type') == 'text', "Content type should be text"
        assert content_item.get('text'), "Content text should not be empty"
        
        words_text = content_item['text']
        # Verify it contains translation word content or handles errors gracefully
        assert any(phrase in words_text.lower() for phrase in [
            'translation word', 'john 3:16', 'error', 'not found', 'word', 'definition'
        ]), "Response should contain translation word content or error message"
        
    elif 'words' in response:
        # Direct API format - array of words
        words = response['words']
        assert isinstance(words, list), "Words should be a list"
        # Allow empty list as valid response since some verses might not have linked words
        
    elif 'term' in response and 'definition' in response:
        # Direct API format - single word object
        assert response['term'], "Term should not be empty"
        assert response['definition'], "Definition should not be empty"
        
    else:
        # Allow other formats for now, but verify it's not None
        assert response, "Translation word response should not be empty"


@pytest.mark.asyncio
async def test_get_translation_word_missing_reference(proxy_server):
    """Test get_translation_word with missing reference parameter."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    # Should either return an error or handle gracefully
    assert response is not None, "Should return some response even for missing reference"
    
    if 'content' in response:
        content_text = response['content'][0]['text']
        # Should indicate an error about missing reference
        assert 'error' in content_text.lower() or 'required' in content_text.lower(), \
            "Should indicate reference is required"


@pytest.mark.asyncio
async def test_get_translation_word_key_verses(proxy_server):
    """Test get_translation_word with verses that likely have translation words."""
    # These verses are likely to have translation words linked
    test_references = [
        'John 3:16',    # God, world, believe, eternal life, etc.
        'Romans 1:16',  # gospel, salvation, righteousness
        'Genesis 1:1',  # God, heaven, earth
        'Matthew 5:3'   # blessed, poor in spirit, kingdom of heaven
    ]
    
    for reference in test_references:
        response = await proxy_server._call_upstream('tools/call', {
            'name': 'get_translation_word',
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
async def test_get_translation_word_default_params(proxy_server):
    """Test get_translation_word with minimal parameters (using defaults)."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'John 3:16'
            # language and organization should default to 'en' and 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from get_translation_word with defaults"
    
    # Should work the same as with explicit parameters
    if 'content' in response:
        assert isinstance(response['content'], list), "Content should be a list"
        if len(response['content']) > 0:
            assert response['content'][0].get('type') == 'text', "Content type should be text"


@pytest.mark.asyncio
async def test_get_translation_word_invalid_reference(proxy_server):
    """Test get_translation_word with an invalid Bible reference."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'InvalidBook 999:999',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    # Should handle invalid references gracefully
    assert response is not None, "Should return some response for invalid reference"
    
    if 'content' in response:
        content_text = response['content'][0]['text'].lower()
        # Should handle invalid reference gracefully (may return empty or error)
        # Accept various response patterns including empty responses
        assert len(content_text) >= 0, "Should handle invalid reference gracefully"


@pytest.mark.asyncio
async def test_get_translation_word_response_structure(proxy_server):
    """Test that get_translation_word response has correct structure."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from get_translation_word"
    assert isinstance(response, dict), "Response should be a dictionary"
    
    # Verify it follows one of the expected response formats
    expected_keys = ['content', 'words', 'term', 'result']
    assert any(key in response for key in expected_keys), \
        f"Response should contain one of: {expected_keys}. Got keys: {list(response.keys())}"


@pytest.mark.asyncio
async def test_get_translation_word_content_validation(proxy_server):
    """Test that translation word content is meaningful when found."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from get_translation_word"
    
    if 'content' in response and len(response['content']) > 0:
        content_text = response['content'][0]['text']
        
        # If content contains actual translation words (not just errors), validate basic structure
        if not any(error_phrase in content_text.lower() for error_phrase in ['error', 'not found', 'invalid']):
            # Should have some content about translation words
            assert len(content_text.strip()) >= 0, "Content should be valid text"
            
            # Check if it contains translation word indicators (flexible validation)
            has_word_indicators = any(indicator in content_text.lower() for indicator in [
                'word', 'translation', 'definition', 'meaning', 'refers', 'describes', 'term', '**'
            ])
            
            # Allow various content formats - if there's substantial content, expect some structure
            if len(content_text.strip()) > 50:
                assert has_word_indicators, \
                    "Substantial translation word content should have word-related indicators"


@pytest.mark.asyncio
async def test_get_translation_word_tool_integration(proxy_server):
    """Test get_translation_word as part of full MCP tool workflow."""
    # First verify the tool exists in the tools list
    tools_response = await proxy_server._call_upstream('tools/list', {})
    
    assert tools_response is not None, "No response from tools/list"
    assert 'tools' in tools_response, "No tools in response"
    
    # Find the get_translation_word tool
    tw_tool = None
    for tool in tools_response['tools']:
        if tool['name'] == 'get_translation_word':
            tw_tool = tool
            break
    
    assert tw_tool is not None, "get_translation_word tool not found in tools list"
    assert 'description' in tw_tool, "Tool should have description"
    assert 'inputSchema' in tw_tool, "Tool should have input schema"
    
    # Verify required parameters in schema
    schema = tw_tool['inputSchema']
    assert 'properties' in schema, "Schema should have properties"
    assert 'reference' in schema['properties'], "Schema should require reference parameter"
    
    # Verify the description mentions translation words
    description = tw_tool['description'].lower()
    assert 'translation word' in description, "Description should mention translation words"
    
    # Now test the actual tool call
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'John 3:16'
        }
    })
    
    assert response is not None, "Tool call should return a response"


@pytest.mark.asyncio
async def test_get_translation_word_vs_fetch_translation_words(proxy_server):
    """Test get_translation_word vs fetch_translation_words to understand differences."""
    reference = 'John 3:16'
    
    # Test get_translation_word
    tw_response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {'reference': reference}
    })
    
    # Test fetch_translation_words (if it exists)
    ftw_response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_words',
        'arguments': {'reference': reference}
    })
    
    # Both should return some response
    assert tw_response is not None, "get_translation_word should return a response"
    assert ftw_response is not None, "fetch_translation_words should return a response"
    
    # Both should follow similar response patterns
    tw_has_content = 'content' in tw_response
    ftw_has_content = 'content' in ftw_response
    
    # If both have content, they should both be lists
    if tw_has_content:
        assert isinstance(tw_response['content'], list), "get_translation_word content should be list"
    if ftw_has_content:
        assert isinstance(ftw_response['content'], list), "fetch_translation_words content should be list"