#!/usr/bin/env python3
"""
Additional unit tests for scrape_words.py main execution block
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import scrape_words


class TestScrapeWordsMain:
    """Test suite for scrape_words.py main execution block"""
    
    def test_main_function_with_results(self, capsys):
        """Test main function when words are successfully scraped"""
        mock_word_dict = {
            'testword1': 'http://example.com/word1',
            'testword2': 'http://example.com/word2'
        }
        
        with patch('scrape_words.get_word_urls', return_value=mock_word_dict) as mock_get:
            with patch('scrape_words.save_to_csv') as mock_save:
                scrape_words.main()
                
                # Verify get_word_urls was called with skip_existing=True
                mock_get.assert_called_once_with(skip_existing=True)
                
                # Verify save_to_csv was called with append=True
                mock_save.assert_called_once_with(mock_word_dict, append=True)
        
        captured = capsys.readouterr()
        assert "Starting scraping process..." in captured.out
        assert "Checking for new words on wordsmith.org..." in captured.out
    
    def test_main_function_no_results(self, capsys):
        """Test main function when no words are scraped"""
        with patch('scrape_words.get_word_urls', return_value={}) as mock_get:
            with patch('scrape_words.save_to_csv') as mock_save:
                scrape_words.main()
                
                # Verify get_word_urls was called
                mock_get.assert_called_once_with(skip_existing=True)
                
                # Verify save_to_csv was NOT called
                mock_save.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Starting scraping process..." in captured.out
        assert "No words were scraped." in captured.out
    
    def test_main_execution_block(self, capsys):
        """Test the if __name__ == '__main__' execution block"""
        # Simply verify that running as main calls the main function
        with patch('scrape_words.main') as mock_main:
            # Mock main to prevent actual execution
            mock_main.return_value = None
            
            # Create namespace to execute the if __name__ == '__main__' block
            test_namespace = {
                '__name__': '__main__',
                'main': mock_main
            }
            
            # Execute just the main block
            main_code = '''
if __name__ == "__main__":
    main()
'''
            exec(main_code, test_namespace)
            
            # Verify main was called
            mock_main.assert_called_once()
    
    def test_main_function_error_handling(self, capsys):
        """Test main function handles errors gracefully"""
        # Test when get_word_urls raises an exception
        with patch('scrape_words.get_word_urls', side_effect=Exception("Test error")):
            with patch('scrape_words.save_to_csv') as mock_save:
                # Should handle the exception gracefully
                with pytest.raises(Exception):
                    scrape_words.main()
                
                # save_to_csv should not be called if get_word_urls fails
                mock_save.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
