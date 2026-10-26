import unittest
from unittest.mock import patch, MagicMock
import os


from src.controller import RegistrationController
from src.registration import RegistrationValidator
from src.database import DatabaseManager
from src.user_interface import UserInterface
from src.external_service import ExternalService


class TestRegistrationIntegration(unittest.TestCase):
    """Интеграционные тесты контроллера с реальными зависимостями (кроме UI и сервиса)."""

    def setUp(self):
        self.test_db = "test_registrations.db"
        self.validator = RegistrationValidator()
        self.db = DatabaseManager(db_name=self.test_db)

        # Создаем моки для UI и внешнего сервиса
        self.mock_ui = MagicMock(spec=UserInterface)
        self.mock_service = MagicMock(spec=ExternalService)

        self.controller = RegistrationController(
            validator=self.validator,
            db=self.db,
            ui=self.mock_ui,
            service=self.mock_service
        )

    def tearDown(self):
        # Сначала закрываем менеджер БД
        if hasattr(self, 'db'):
            # Принудительно удаляем файл, даже если он занят
            try:
                del self.db
            except Exception:
                pass

        import time
        time.sleep(0.1)  # Небольшая пауза для освобождения файла в Windows

        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                print(f"⚠️ Не удалось удалить {self.test_db}, файл занят")

    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 1: Успешная регистрация новых данных ---
    def test_successful_new_registration(self):
        self.mock_ui.get_input.side_effect = ["user_test_1", "Пароль1!кИр", "Пароль1!кИр"]

        result = self.controller.process_registration()

        self.assertTrue(result.startswith("True"), f"Ожидался True, получен: {result}")
        self.mock_service.send_data.assert_called_once()
        record = self.db.get_record("user_test_1", "Пароль1!кИр", "Пароль1!кИр")
        self.assertIsNotNone(record)
        self.assertEqual(record[0], "True")

    def test_cached_registration_result(self):
        # Первый раз регистрируем
        self.mock_ui.get_input.side_effect = ["cached_user", "Тест2@абвгд", "Тест2@абвгд"]
        self.controller.process_registration()

        # Второй раз те же данные - должно взять из кэша
        self.mock_ui.get_input.side_effect = ["cached_user", "Тест2@абвгд", "Тест2@абвгд"]
        result2 = self.controller.process_registration()

        self.assertTrue(result2.startswith("True"), f"Кэш вернул: {result2}")
        self.assertEqual(self.mock_service.send_data.call_count, 2)

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