import os
import sys
import unittest

# чтобы импорты src.* работали при запуске из корня проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):
    def setUp(self):
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repo.close()

    # =================== add ===================
    def test_add_success(self):
        self.assertTrue(self.repo.add(1, "alice", "hello"))
        self.assertIsNotNone(self.repo.get_by_id(1))

    def test_add_duplicate_id_raises(self):
        self.repo.add(1, "alice", "hello")
        with self.assertRaises(ValueError):
            self.repo.add(1, "bob", "hi")

    def test_add_invalid_username_length(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "", "hello")
        with self.assertRaises(ValueError):
            self.repo.add(1, "a" * 257, "hello")

    def test_add_invalid_message_length(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "alice", "")
        with self.assertRaises(ValueError):
            self.repo.add(1, "alice", "x" * 8097)

    def test_add_invalid_types(self):
        with self.assertRaises(TypeError):
            self.repo.add("1", "alice", "hello")   # id — не int
        with self.assertRaises(TypeError):
            self.repo.add(1, 123, "hello")         # name — не str

    # =================== get_by_id ===================
    def test_get_by_id_exists(self):
        self.repo.add(1, "alice", "hello")
        row = self.repo.get_by_id(1)
        self.assertEqual(row["id"], 1)
        self.assertEqual(row["name"], "alice")
        self.assertEqual(row["message"], "hello")

    def test_get_by_id_not_exists(self):
        self.assertIsNone(self.repo.get_by_id(999))

    # =================== get_by_name ===================
    def test_get_by_name_multiple(self):
        self.repo.add(1, "alice", "hi")
        self.repo.add(2, "alice", "hello")
        self.repo.add(3, "bob", "hey")
        rows = self.repo.get_by_name("alice")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["name"] == "alice" for r in rows))

    def test_get_by_name_empty(self):
        self.assertEqual(self.repo.get_by_name("nobody"), [])

    # =================== update ===================
    def test_update_success(self):
        self.repo.add(1, "alice", "old")
        self.assertTrue(self.repo.update(1, "new"))
        self.assertEqual(self.repo.get_by_id(1)["message"], "new")

    def test_update_nonexistent_returns_false(self):
        self.assertFalse(self.repo.update(999, "new"))

    def test_update_invalid_length(self):
        self.repo.add(1, "alice", "old")
        with self.assertRaises(ValueError):
            self.repo.update(1, "")

    # =================== delete ===================
    def test_delete_success(self):
        self.repo.add(1, "alice", "hi")
        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_nonexistent_returns_false(self):
        self.assertFalse(self.repo.delete(999))


if __name__ == "__main__":
    unittest.main()