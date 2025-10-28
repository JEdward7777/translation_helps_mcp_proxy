"""Test filtering of book and chapter-level notes from translation notes responses."""

import pytest


@pytest.mark.asyncio
async def test_fetch_translation_notes_without_filtering(proxy_server):
    """Test that without filtering, book and chapter notes are included."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None
    assert 'items' in response
    items = response['items']
    
    # Without filtering, we should have book-level notes (front:intro)
    book_notes = [item for item in items if item.get('Reference') == 'front:intro']
    assert len(book_notes) > 0, "Should include book-level notes without filtering"
    assert '# Introduction to John' in book_notes[0]['Note']
    
    # And chapter-level notes (3:intro)
    chapter_notes = [item for item in items if item.get('Reference') == '3:intro']
    assert len(chapter_notes) > 0, "Should include chapter-level notes without filtering"
    assert '# John 3 Chapter Introduction' in chapter_notes[0]['Note']
    
    # And verse-specific notes (3:16)
    verse_notes = [item for item in items if item.get('Reference') == '3:16']
    assert len(verse_notes) > 0, "Should include verse-specific notes"


@pytest.mark.asyncio
async def test_fetch_translation_notes_with_filtering(proxy_server_with_filtering):
    """Test that with filtering enabled, book and chapter notes are excluded."""
    response = await proxy_server_with_filtering._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None
    assert 'items' in response
    items = response['items']
    
    # With filtering, book-level notes should be removed
    book_notes = [item for item in items if item.get('Reference') == 'front:intro']
    assert len(book_notes) == 0, "Should exclude book-level notes with filtering"
    
    # Chapter-level notes should also be removed
    chapter_notes = [item for item in items if item.get('Reference') == '3:intro']
    assert len(chapter_notes) == 0, "Should exclude chapter-level notes with filtering"
    
    # But verse-specific notes should remain
    verse_notes = [item for item in items if item.get('Reference') == '3:16']
    assert len(verse_notes) > 0, "Should still include verse-specific notes"
    
    # Verify the total count is reduced
    assert len(items) < 9, "Filtered response should have fewer items than unfiltered"


@pytest.mark.asyncio
async def test_note_filtering_multiple_verses_same_chapter(proxy_server_with_filtering):
    """Test that filtering works correctly across multiple verses in the same chapter."""
    # Fetch notes for two different verses in John 3
    references = ['John 3:16', 'John 3:17']
    
    for reference in references:
        response = await proxy_server_with_filtering._call_upstream('tools/call', {
            'name': 'fetch_translation_notes',
            'arguments': {
                'reference': reference,
                'language': 'en',
                'organization': 'unfoldingWord'
            }
        })
        
        assert response is not None
        assert 'items' in response
        items = response['items']
        
        # Neither should have book or chapter notes
        book_notes = [item for item in items if item.get('Reference') == 'front:intro']
        chapter_notes = [item for item in items if item.get('Reference') == '3:intro']
        
        assert len(book_notes) == 0, f"No book notes for {reference}"
        assert len(chapter_notes) == 0, f"No chapter notes for {reference}"


@pytest.mark.asyncio
async def test_note_filtering_different_chapters(proxy_server_with_filtering):
    """Test that filtering works correctly across different chapters."""
    # Test different chapters to ensure chapter-level filtering is chapter-specific
    references = ['John 3:16', 'John 4:1']
    
    for reference in references:
        response = await proxy_server_with_filtering._call_upstream('tools/call', {
            'name': 'fetch_translation_notes',
            'arguments': {
                'reference': reference,
                'language': 'en',
                'organization': 'unfoldingWord'
            }
        })
        
        assert response is not None
        assert 'items' in response
        items = response['items']
        
        # No book-level notes
        book_notes = [item for item in items if item.get('Reference') == 'front:intro']
        assert len(book_notes) == 0, f"No book notes for {reference}"
        
        # No chapter-level notes (regardless of which chapter)
        chapter_notes = [item for item in items if ':intro' in item.get('Reference', '')]
        assert len(chapter_notes) == 0, f"No chapter intro notes for {reference}"


@pytest.mark.asyncio
async def test_note_filtering_preserves_metadata(proxy_server_with_filtering):
    """Test that filtering preserves metadata and only modifies items."""
    response = await proxy_server_with_filtering._call_upstream('tools/call', {
        'name': 'fetch_translation_notes',
        'arguments': {
            'reference': 'John 3:16',
            'language': 'en',
            'organization': 'unfoldingWord'
        }
    })
    
    assert response is not None
    assert 'metadata' in response
    assert 'reference' in response
    assert 'language' in response
    assert 'organization' in response
    
    # Metadata should be preserved
    assert response['reference'] == 'John 3:16'
    assert response['language'] == 'en'
    assert response['organization'] == 'unfoldingWord'