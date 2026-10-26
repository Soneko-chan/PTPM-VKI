import logging
import re
import os
import hashlib

# Настройка логирования
log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.WARNING,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/file_txt.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("RegistrationValidator")

LoginBlacklist = ["admin", "root", "user", "test", "support", "moderator"]


class RegistrationValidator:

    @staticmethod
    def mask_password(password):
        if not password:
            return "EMPTY"
        return hashlib.sha256(password.encode('utf-8')).hexdigest()[:16] + "..."

    @staticmethod
    def validate_login_format(login):
        phone_pattern = r'^\+\d-\d{3}-\d{3}-\d{4}$'
        if re.match(phone_pattern, login):
            return True, "Phone"

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, login):
            return True, "Email"

        string_pattern = r'^[a-zA-Z0-9_]{5,}$'
        if re.match(string_pattern, login):
            return True, "String"

        return False, "InvalidFormat"

    @staticmethod
    def check_blacklist(login):
        return login.lower() in [b.lower() for b in LoginBlacklist]

    @staticmethod
    def validate_password_complexity(password):
        if len(password) < 7:
            return False, "PasswordTooShort"

        allowed_chars_pattern = r'^[А-Яа-яЁё0-9!@#$%^&*()_+\-=\[\]{}\\|;:\'",.<>/?`~]+$'
        if not re.match(allowed_chars_pattern, password):
            return False, "PasswordContainsForbiddenChars"

        has_upper = bool(re.search(r'[А-ЯЁ]', password))
        has_lower = bool(re.search(r'[а-яё]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^А-Яа-яЁё0-9]', password))

        if not has_upper:
            return False, "NoUppercaseLetter"
        if not has_lower:
            return False, "NoLowercaseLetter"
        if not has_digit:
            return False, "NoDigit"
        if not has_special:
            return False, "NoSpecialChar"

        return True, "OK"

    def register_user(self, login, password, confirm_password):
        logger.info(f"Начало регистрации. Логин: '{login}', Пароль (хеш): {self.mask_password(password)}")

        try:
            if password != confirm_password:
                msg = "Пароли не совпадают"
                logger.warning(f"Ошибка валидации: {msg}")
                return "False", msg

            is_valid_format, login_type = self.validate_login_format(login)
            if not is_valid_format:
                msg = "Неверный формат логина"
                logger.warning(f"Ошибка валидации логина: {msg}")
                return "False", msg

            if self.check_blacklist(login):
                msg = f"Логин '{login}' находится в черном списке"
                logger.warning(f"Ошибка валидации логина: {msg}")
                return "False", msg

            is_pass_valid, pass_err_code = self.validate_password_complexity(password)
            if not is_pass_valid:
                error_messages = {
                    "PasswordTooShort": "Пароль слишком короткий (минимум 7 символов)",
                    "PasswordContainsForbiddenChars": "Пароль содержит запрещенные символы",
                    "NoUppercaseLetter": "Пароль должен содержать заглавную букву (кириллица)",
                    "NoLowercaseLetter": "Пароль должен содержать строчную букву (кириллица)",
                    "NoDigit": "Пароль должен содержать цифру",
                    "NoSpecialChar": "Пароль должен содержать спецсимвол"
                }
                msg = error_messages.get(pass_err_code, "Ошибка сложности пароля")
                logger.warning(f"Ошибка валидации пароля: {msg}")
                return "False", msg

            logger.info(f"Регистрация успешна для пользователя: {login}")
            return "True", ""

        except Exception as e:
            logger.error("Произошла непредвиденная ошибка при регистрации:")
            logger.exception(e)
            return "False", "Внутренняя ошибка сервера"