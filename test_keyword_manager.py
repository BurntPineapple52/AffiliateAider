from reddit_affiliate_bot.modules.keyword_manager import KeywordManager

def test_keyword_manager():
    km = KeywordManager()
    km.load_keywords(['test1', 'test2'])
    print(km.get_next_keyword())

if __name__ == "__main__":
    test_keyword_manager()
