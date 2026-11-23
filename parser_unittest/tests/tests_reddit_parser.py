import os
import unittest

from src.parser import ForumParser


@unittest.skipUnless(os.getenv("RUN_LIVE_TESTS") == "1",
                     "нужен интернет: RUN_LIVE_TESTS=1")
class TestRedditLive(unittest.TestCase):
    def test_real_post(self):
        posts = ForumParser().parse_reddit_post(
            "https://www.reddit.com/r/OtvetMailRUS/comments/1y1x34g/%D1%85%D0%BE%D1%87%D1%83_%D0%B6%D1%80%D0%B0%D1%82%D1%8C_%D0%BA%D0%B0%D0%BA_%D0%BA%D0%B0%D0%B1%D0%B0%D0%BD_%D1%82%D1%80%D0%B0%D1%85%D0%B0%D1%82%D1%8C%D1%81%D1%8F_%D1%81_%D0%BC%D0%B8%D0%BB%D1%84%D0%BE%D0%B9_%D0%BA%D0%B0%D0%BA/.json"
        )
        self.assertGreater(len(posts), 0)
        self.assertTrue(posts[0]["name"])