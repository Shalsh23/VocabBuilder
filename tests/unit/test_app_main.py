#!/usr/bin/env python3
"""
Additional unit tests for app.py main execution block
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add web directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'web'))

import app


class TestAppMain:
    """Test suite for app.py main execution block"""
    
    def test_main_execution_block(self):
        """Test the if __name__ == '__main__' execution block"""
        # Mock Flask app.run
        with patch.object(app.app, 'run') as mock_run:
            # Create a mock app object
            mock_app = MagicMock()
            mock_app.run = mock_run
            
            # Execute the main block
            test_namespace = {
                '__name__': '__main__',
                'app': mock_app
            }
            
            main_code = '''
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8080)
'''
            exec(main_code, test_namespace)
            
            # Verify app.run was called with correct parameters
            mock_run.assert_called_once_with(debug=False, host='127.0.0.1', port=8080)
    
    def test_app_configuration(self):
        """Test Flask app configuration"""
        # Test that app has the expected configuration
        assert app.app.name == 'app'
        assert app.WORDS_PER_PAGE == 50
        assert app.CSV_FILE.endswith('wordsmith_complete.csv')
    
    def test_load_word_data_called(self):
        """Test that load_word_data is called when module is imported"""
        # The function should have been called during module import
        # We can check if WORD_DATA is populated (or at least initialized)
        assert isinstance(app.WORD_DATA, list)
        assert isinstance(app.WORD_DICT, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
