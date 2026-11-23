import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser_unittest.src.parser import ForumParser
from parser_unittest.src.database import DatabaseRepository

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestForumParser(unittest.TestCase):
    def setUp(self):
        self.parser = ForumParser()
        posts = parser.parse_reddit_post(
            "https://www.reddit.com/r/OtvetMailRUS/comments/1y1x34g/%D1%85%D0%BE%D1%87%D1%83_%D0%B6%D1%80%D0%B0%D1%82%D1%8C_%D0%BA%D0%B0%D0%BA_%D0%BA%D0%B0%D0%B1%D0%B0%D0%BD_%D1%82%D1%80%D0%B0%D1%85%D0%B0%D1%82%D1%8C%D1%81%D1%8F_%D1%81_%D0%BC%D0%B8%D0%BB%D1%84%D0%BE%D0%B9_%D0%BA%D0%B0%D0%BA/"
        )

    # --- parse_html ---
    def test_parse_html_extracts_only_valid_posts(self):
        posts = self.parser.parse_html(self.html)
        self.assertEqual(len(posts), 3)

    def test_parse_html_fields_are_correct(self):
        posts = self.parser.parse_html(self.html)
        first = posts[0]
        self.assertEqual(first["id"], 101)
        self.assertEqual(first["name"], "alice")
        # внутренняя HTML-разметка сохраняется
        self.assertIn("<b>world</b>", first["message"])

    def test_parse_html_empty_page(self):
        posts = self.parser.parse_html("<html><body></body></html>")
        self.assertEqual(posts, [])

    # --- save_to_db ---
    def test_save_to_db_persists_all(self):
        repo = DatabaseRepository(":memory:")
        try:
            posts = self.parser.parse_html(self.html)
            saved = self.parser.save_to_db(posts, repo)
            self.assertEqual(saved, 3)
            self.assertEqual(len(repo.get_by_name("alice")), 2)
            self.assertEqual(len(repo.get_by_name("bob")), 1)
        finally:
            repo.close()

    def test_save_to_db_skips_duplicates(self):
        repo = DatabaseRepository(":memory:")
        try:
            posts = self.parser.parse_html(self.html)
            self.parser.save_to_db(posts, repo)
            saved = self.parser.save_to_db(posts, repo)
            self.assertEqual(saved, 0)
        finally:
            repo.close()


if __name__ == "__main__":
    unittest.main()