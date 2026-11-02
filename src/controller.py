from src.registration import RegistrationValidator
from src.database import DatabaseManager
from src.user_interface import UserInterface
from src.external_service import ExternalService


class RegistrationController:

    def __init__(self, validator: RegistrationValidator, db: DatabaseManager,
                 ui: UserInterface, service: ExternalService):
        self.validator = validator
        self.db = db
        self.ui = ui
        self.service = service

    def process_registration(self) -> str:

        login = self.ui.get_input("Введите логин: ")
        password = self.ui.get_input("Введите пароль: ")
        confirm_password = self.ui.get_input("Подтвердите пароль: ")


        cached = self.db.get_record(login, password, confirm_password)

        if cached:
            result, message = cached

            output_data = f"Login:{login} | Result:{result} | Msg:{message}"
            self.service.send_data(output_data)
            return f"{result}|{message}"

        result, message = self.validator.register_user(login, password, confirm_password)
        self.db.add_record(login, password, confirm_password, result, message)

        output_data = f"Login:{login} | Result:{result} | Msg:{message}"
        self.service.send_data(output_data)

      
        return f"{result}|{message}"