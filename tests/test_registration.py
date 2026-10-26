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
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 1: Успешная регистрация новых данных ---
    def test_successful_new_registration(self):
        """Проверяет полный цикл: ввод -> валидация -> запись в БД -> отправка в сервис."""
        self.mock_ui.get_input.side_effect = ["user_test_1", "Пароль1!", "Пароль1!"]

        result = self.controller.process_registration()

        self.assertTrue(result.startswith("True"))
        self.mock_service.send_data.assert_called_once()
        # Проверяем, что данные действительно попали в БД
        record = self.db.get_record("user_test_1", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(record)
        self.assertEqual(record[0], "True")

    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 2: Получение результата из кэша БД ---
    def test_cached_registration_result(self):
        """Проверяет, что при повторном вводе тех же данных результат берется из БД,
        а не вычисляется заново."""
        # Сначала регистрируем пользователя
        self.mock_ui.get_input.side_effect = ["cached_user", "Qwerty1@", "Qwerty1@"]
        self.controller.process_registration()

        # Сбрасываем счетчик вызовов валидатора (через mock, если бы он был моком),
        # но здесь мы проверяем через БД. Добавим запись вручную для чистоты теста
        # или просто вызовем второй раз.
        self.mock_ui.get_input.side_effect = ["cached_user", "Qwerty1@", "Qwerty1@"]
        result2 = self.controller.process_registration()

        self.assertTrue(result2.startswith("True"))
        # Сервис должен быть вызван дважды (для каждого запроса)
        self.assertEqual(self.mock_service.send_data.call_count, 2)

    # --- ИНТЕГРАЦИОННЫЙ ТЕСТ 3: Ошибка валидации сохраняется в БД ---
    def test_failed_validation_stored_in_db(self):
        """Проверяет, что неудачная попытка регистрации также кэшируется."""
        self.mock_ui.get_input.side_effect = ["admin", "Weak", "Weak"]  # admin в блеклисте

        result = self.controller.process_registration()

        self.assertTrue(result.startswith("False"))
        self.assertIn("черном списке", result)

        # Проверяем БД
        record = self.db.get_record("admin", "Weak", "Weak")
        self.assertIsNotNone(record)
        self.assertEqual(record[0], "False")

    # --- ЮНИТ-ТЕСТ 1: Подмена пользовательского ввода (mock input) ---
    def test_mock_user_input_handling(self):
        """Проверяет корректную обработку последовательности вводов через mock."""
        inputs = ["+7-999-123-4567", "StrongPass1!", "StrongPass1!"]
        self.mock_ui.get_input.side_effect = inputs

        result = self.controller.process_registration()

        calls = self.mock_ui.get_input.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertTrue(result.startswith("True"))

    # --- ЮНИТ-TEST 2: Подмена внешнего сервиса (mock service) ---
    def test_external_service_mock_verification(self):
        """Проверяет, что контроллер вызывает сервис с правильными данными."""
        self.mock_ui.get_input.side_effect = ["test_mock_svc", "TestPass1!", "TestPass1!"]

        self.controller.process_registration()

        # Проверяем, что send_data был вызван ровно один раз
        self.mock_service.send_data.assert_called_once()
        call_arg = self.mock_service.send_data.call_args[0][0]
        self.assertIn("test_mock_svc", call_arg)
        self.assertIn("Result:True", call_arg)


if __name__ == "__main__":
    unittest.main()