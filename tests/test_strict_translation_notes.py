"""Strict test for fetch_translation_notes that expects actual content, not errors."""

import pytest
import json


@pytest.mark.asyncio
async def test_fetch_translation_notes_expects_content(proxy_server):
    """Test that expects actual translation notes content, will fail on errors."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from fetch_translation_notes"
    
    # DEBUG: Print what we actually got
    print(f"\n=== DEBUG fetch_translation_notes response ===")
    print(f"Response keys: {list(response.keys()) if response else 'None'}")
    print(f"Full response: {json.dumps(response, indent=2) if response else 'None'}")
    print("=" * 50)
    
    # This test expects actual translation notes content, not error messages
    if 'content' in response:
        assert isinstance(response['content'], list), "Content should be a list"
        assert len(response['content']) > 0, "Content list should not be empty"
        
        content_item = response['content'][0]
        assert content_item.get('type') == 'text', "Content type should be text"
        assert content_item.get('text'), "Content text should not be empty"
        
        notes_text = content_item['text']
        
        # This should FAIL if we get error messages
        assert 'invalid url' not in notes_text.lower(), "Should not get invalid URL error"
        assert 'error' not in notes_text.lower(), "Should not get error messages"
        
        # This should PASS only if we get actual translation notes content
        assert any(phrase in notes_text.lower() for phrase in [
            'translation', 'note', 'john 3:16', 'verse', 'commentary'
        ]), "Should contain actual translation notes content"
        
    else:
        pytest.fail("Response should contain 'content' field with translation notes")


@pytest.mark.asyncio  
async def test_get_translation_word_expects_content(proxy_server):
    """Test that expects actual translation word content, will fail on errors."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_translation_word',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None, "No response from get_translation_word"
    
    # DEBUG: Print what we actually got
    print(f"\n=== DEBUG get_translation_word response ===")
    print(f"Response keys: {list(response.keys()) if response else 'None'}")
    print(f"Full response: {json.dumps(response, indent=2) if response else 'None'}")
    print("=" * 50)
    
    # This test expects actual translation word content, not error messages
    if 'content' in response:
        content_item = response['content'][0]
        content_text = content_item['text']
        
        # This should FAIL if we get error messages
        assert 'missing required parameter' not in content_text.lower(), "Should not get missing parameter error"
        assert 'error' not in content_text.lower(), "Should not get error messages"
        
        # This should PASS only if we get actual translation word content
        assert any(phrase in content_text.lower() for phrase in [
            'word', 'definition', 'term', 'translation', 'meaning'
        ]), "Should contain actual translation word content"
        
    else:
        pytest.fail("Response should contain 'content' field with translation words")