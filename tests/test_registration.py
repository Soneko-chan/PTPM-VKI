import unittest
from unittest.mock import MagicMock
import os

from src.controller import RegistrationController
from src.registration import RegistrationValidator
from src.database import DatabaseManager
from src.user_interface import UserInterface
from src.external_service import ExternalService


class TestRegistrationIntegration(unittest.TestCase):

    def setUp(self):

        self.test_db = ":memory:"
        self.validator = RegistrationValidator()
        self.db = DatabaseManager(db_name=self.test_db)

        self.mock_ui = MagicMock(spec=UserInterface)
        self.mock_service = MagicMock(spec=ExternalService)


        self.controller = RegistrationController(
            validator=self.validator,
            db=self.db,
            ui=self.mock_ui,
            service=self.mock_service
        )

    def tearDown(self):
        # Явно закрываем соединение
        if hasattr(self, 'db'):
            self.db.close()

    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 1 ---
    def test_successful_new_registration(self):
        self.mock_ui.get_input.side_effect = ["user_test_1", "Пароль1!кИр", "Пароль1!кИр"]

        result = self.controller.process_registration()

        self.assertTrue(result.startswith("True"), f"Ожидался True, получен: {result}")
        self.mock_service.send_data.assert_called_once()
        record = self.db.get_record("user_test_1", "Пароль1!кИр", "Пароль1!кИр")
        self.assertIsNotNone(record)
        self.assertEqual(record[0], "True")

    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 2 ---
    def test_cached_registration_result(self):
        mock_validator = MagicMock(spec=RegistrationValidator)

        mock_validator.register_user.return_value = ("True", "")

        self.controller = RegistrationController(
            validator=mock_validator,
            db=self.db,
            ui=self.mock_ui,
            service=self.mock_service
        )
        self.mock_ui.get_input.side_effect = ["cached_user", "Тест2@абвгд", "Тест2@абвгд"]
        result1 = self.controller.process_registration()

        self.assertEqual(mock_validator.register_user.call_count, 1,
                         "Валидатор должен вызваться при первой регистрации")

        self.mock_ui.get_input.side_effect = ["cached_user", "Тест2@абвгд", "Тест2@абвгд"]
        result2 = self.controller.process_registration()

        self.assertEqual(mock_validator.register_user.call_count, 1,
                         "Валидатор не должен вызываться при чтении из кэша")

        self.assertEqual(result1, result2, "Результаты не совпадают")
        self.assertTrue(result2.startswith("True"), f"Кэш вернул: {result2}")


    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 3 ---
    def test_failed_validation_stored_in_db(self):
        self.mock_ui.get_input.side_effect = ["admin", "Weak", "Weak"]

        result = self.controller.process_registration()

        self.assertTrue(result.startswith("False"))
        self.assertIn("черном списке", result)

        record = self.db.get_record("admin", "Weak", "Weak")
        self.assertIsNotNone(record)
        self.assertEqual(record[0], "False")

    # --- ЮНИТ-ТЕСТ 1 ---
    def test_mock_user_input_handling(self):
        inputs = ["+7-999-123-4567", "Пароль1!кИр", "Пароль1!кИр"]
        self.mock_ui.get_input.side_effect = inputs

        result = self.controller.process_registration()

        calls = self.mock_ui.get_input.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertTrue(result.startswith("True"), f"Результат: {result}")


    def test_external_service_mock_verification(self):
        self.mock_ui.get_input.side_effect = ["test_mock_svc", "Тест2@абвгд", "Тест2@абвгд"]

        self.controller.process_registration()

        self.mock_service.send_data.assert_called_once()
        call_arg = self.mock_service.send_data.call_args[0][0]
        self.assertIn("test_mock_svc", call_arg)
        self.assertIn("Result:True", call_arg, f"Аргумент сервиса: {call_arg}")


if __name__ == "__main__":
    unittest.main()