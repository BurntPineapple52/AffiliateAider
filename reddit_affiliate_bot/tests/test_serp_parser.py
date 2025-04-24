import unittest
from reddit_affiliate_bot.modules.serp_parser import SERPParser

class TestSERPParser(unittest.TestCase):
    def test_extract_reddit_urls(self):
        test_data = [{'link': 'https://www.reddit.com/r/AskReddit/comments/abc123/sample_post/'}]
        expected = ['https://www.reddit.com/r/AskReddit/comments/abc123/sample_post/']
        result = SERPParser.extract_reddit_urls(test_data)
        self.assertEqual(result, expected)

    def test_extract_thread_ids(self):
        test_urls = ['https://www.reddit.com/r/AskReddit/comments/abc123/sample_post/']
        expected = ['abc123']
        result = SERPParser.extract_thread_ids(test_urls)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
