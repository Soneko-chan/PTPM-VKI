from abc import ABC, abstractmethod


class ExternalService(ABC):


    @abstractmethod
    def send_data(self, data: str) -> bool:

        pass


class EmailNotificationService(ExternalService):


    def send_data(self, data: str) -> bool:
        # Имитация работы внешнего сервиса
        print(f"[EXTERNAL SERVICE] Отправка уведомления: {data}")
        return True