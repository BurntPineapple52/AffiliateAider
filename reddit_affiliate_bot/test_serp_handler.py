import unittest
from unittest.mock import patch, MagicMock
from modules.serp_handler import SERPHandler

class TestSERPHandler(unittest.TestCase):
    @patch('googleapiclient.discovery.build')
    def test_search(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_result = {'items': [{'title': 'Test', 'link': 'http://test.com'}]}
        mock_service.cse().list().execute.return_value = mock_result
        
        handler = SERPHandler('test_key', 'test_id')
        results = handler.search('test query')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test')

    def test_parse_results(self):
        handler = SERPHandler('test_key', 'test_id')
        test_data = [{'title': 'Test', 'link': 'http://test.com', 'snippet': '...'}]
        parsed = handler.parse_results(test_data)
        
        self.assertEqual(parsed[0]['title'], 'Test')
        self.assertEqual(parsed[0]['link'], 'http://test.com')

if __name__ == '__main__':
    unittest.main()
