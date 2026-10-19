import unittest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Registration import (
    register_user,
    validate_login_format,
    check_blacklist,
    validate_password_complexity,
    mask_password,
    LoginBlacklist
)


class TestRegistrationValidator(unittest.TestCase):


    def test_successful_registration_with_string_login(self):

        res, msg = register_user("valid_user_1", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "True")
        self.assertEqual(msg, "")

    def test_passwords_do_not_match(self):

        res, msg = register_user("valid_user_1", "Пароль1!", "Пароль2!")
        self.assertEqual(res, "False")
        self.assertIn("не совпадают", msg.lower())

    def test_login_in_blacklist(self):

        res, msg = register_user("admin", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("черном списке", msg.lower())

    def test_login_too_short(self):

        res, msg = register_user("ab", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("Неверный формат", msg)

    def test_latin_chars_in_password(self):

        res, msg = register_user("new_user_ok", "Password1!", "Password1!")
        self.assertEqual(res, "False")
        self.assertIn("запрещенные символы", msg.lower())

    def test_password_without_special_char(self):

        res, msg = register_user("new_user_ok", "Пароль12", "Пароль12")
        self.assertEqual(res, "False")
        self.assertIn("спецсимвол", msg.lower())

    def test_successful_registration_with_email(self):

        res, msg = register_user("test@example.com", "Секрет9@", "Секрет9@")
        self.assertEqual(res, "True")
        self.assertEqual(msg, "")

    def test_successful_registration_with_phone(self):

        res, msg = register_user("+7-900-123-4567", "МойПароль1#", "МойПароль1#")
        self.assertEqual(res, "True")
        self.assertEqual(msg, "")

    def test_password_too_short(self):

        res, msg = register_user("valid_user_2", "Пар1!", "Пар1!")
        self.assertEqual(res, "False")
        self.assertIn("слишком короткий", msg.lower())

    def test_password_without_uppercase(self):

        res, msg = register_user("valid_user_3", "пароль1!", "пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("заглавную букву", msg.lower())

    def test_password_without_lowercase(self):

        res, msg = register_user("valid_user_4", "ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertEqual(res, "False")
        self.assertIn("строчную букву", msg.lower())

    def test_password_without_digit(self):

        res, msg = register_user("valid_user_5", "Пароль!а", "Пароль!а")
        self.assertEqual(res, "False")
        self.assertIn("цифру", msg.lower())

    def test_blacklist_case_insensitive(self):

        res, msg = register_user("ADMIN", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("черном списке", msg.lower())

    def test_invalid_email_format(self):

        res, msg = register_user("invalid@email", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("Неверный формат", msg)

    def test_invalid_phone_format(self):

        res, msg = register_user("+79001234567", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("Неверный формат", msg)

    def test_validate_login_format_phone(self):

        is_valid, login_type = validate_login_format("+7-900-123-4567")
        self.assertTrue(is_valid)
        self.assertEqual(login_type, "Phone")

    def test_validate_login_format_email(self):

        is_valid, login_type = validate_login_format("user@example.com")
        self.assertTrue(is_valid)
        self.assertEqual(login_type, "Email")

    def test_validate_login_format_string(self):

        is_valid, login_type = validate_login_format("valid_user_name")
        self.assertTrue(is_valid)
        self.assertEqual(login_type, "String")

    def test_validate_login_format_invalid(self):

        is_valid, login_type = validate_login_format("ab")
        self.assertFalse(is_valid)
        self.assertEqual(login_type, "InvalidFormat")

    def test_check_blacklist_positive(self):

        result = check_blacklist("admin")
        self.assertTrue(result)

    def test_check_blacklist_negative(self):

        result = check_blacklist("myusername")
        self.assertFalse(result)

    def test_mask_password_empty(self):

        result = mask_password("")
        self.assertEqual(result, "EMPTY")

    def test_mask_password_returns_hash(self):

        result = mask_password("test_password")
        self.assertNotEqual(result, "EMPTY")
        self.assertTrue(result.endswith("..."))
        self.assertEqual(len(result), 19)

    def test_validate_password_complexity_valid(self):

        is_valid, error_code = validate_password_complexity("Пароль1!")
        self.assertTrue(is_valid)
        self.assertEqual(error_code, "OK")

    def test_validate_password_complexity_too_short(self):

        is_valid, error_code = validate_password_complexity("Пар1!")
        self.assertFalse(is_valid)
        self.assertEqual(error_code, "PasswordTooShort")

    def test_register_with_all_blacklist_items(self):

        for blacklisted_login in LoginBlacklist:
            res, msg = register_user(blacklisted_login, "Пароль1!", "Пароль1!")
            self.assertEqual(res, "False", f"Логин '{blacklisted_login}' должен быть заблокирован")

    def test_password_with_only_cyrillic_and_digits(self):

        res, msg = register_user("valid_user_6", "Пароль12", "Пароль12")
        self.assertEqual(res, "False")
        self.assertIn("спецсимвол", msg.lower())

    def test_empty_login(self):

        res, msg = register_user("", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("Неверный формат", msg)

    def test_login_with_spaces(self):

        res, msg = register_user("valid user", "Пароль1!", "Пароль1!")
        self.assertEqual(res, "False")
        self.assertIn("Неверный формат", msg)

    def test_password_with_whitespace(self):

        res, msg = register_user("valid_user_7", "Пар оль1!", "Пар оль1!")
        self.assertEqual(res, "False")
        self.assertIn("запрещенные символы", msg.lower())


if __name__ == '__main__':
    unittest.main()


