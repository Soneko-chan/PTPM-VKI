import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser import ForumParser
from src.database import DatabaseRepository

# МЕНЯЙ ТОЛЬКО ЭТУ СТРОКУ: вставь ссылку на тему форума, которую хочешь распарсить
FORUM_URL = "https://www.python-forum.de/viewtopic.php?p=437437"


@unittest.skipUnless(os.getenv("RUN_LIVE_TESTS") == "1",
                     "живой тест: RUN_LIVE_TESTS=1")
class TestLiveForum(unittest.TestCase):
    def test_parse_live_forum(self):
        parser = ForumParser()
        posts = parser.parse_page(FORUM_URL)

        self.assertGreater(
            len(posts), 0,
            "парсер ничего не нашёл — у форума другая разметка, нужны новые селекторы",
        )
        self.assertTrue(all(p["id"] and p["name"] and p["message"] for p in posts))

        repo = DatabaseRepository(":memory:")
        try:
            self.assertEqual(parser.save_to_db(posts, repo), len(posts))
        finally:
            repo.close()


if __name__ == "__main__":
    unittest.main()
