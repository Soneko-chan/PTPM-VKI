import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser import ForumParser
from src.database import DatabaseRepository

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestForumParser(unittest.TestCase):
    def setUp(self):
        self.parser = ForumParser()
        with open(os.path.join(FIXTURES_DIR, "sample_page.html"), "r", encoding="utf-8") as f:
            self.html = f.read()

    # --- parse_html ---
    def test_parse_html_extracts_only_valid_posts(self):
        posts = self.parser.parse_html(self.html)
        # в фикстуре 3 валидных + 2 невалидных поста
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
            # второй раз — все 3 уже есть, должно сохраниться 0
            saved = self.parser.save_to_db(posts, repo)
            self.assertEqual(saved, 0)
        finally:
            repo.close()


if __name__ == "__main__":
    unittest.main()