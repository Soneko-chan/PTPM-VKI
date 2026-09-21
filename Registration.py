import logging
import re
import sys
import traceback
import os

log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.WARNING,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/file_txt.log", encoding="utf-8")
    ]
)

logger = logging.getLogger("RegistrationValidator")

LoginBlacklist = ["admin", "root", "user", "test", "support", "moderator"]


def mask_password(password):
    if not password:
        return "EMPTY"
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()[:16] + "..."


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


def check_blacklist(login):
    return login.lower() in [b.lower() for b in LoginBlacklist]


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


def register_user(login, password, confirm_password):
    logger.info(f"Начало регистрации. Логин: '{login}', Пароль (хеш): {mask_password(password)}")

    try:
        if password != confirm_password:
            msg = "Пароли не совпадают"
            logger.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        is_valid_format, login_type = validate_login_format(login)
        if not is_valid_format:
            msg = "Неверный формат логина (должен быть телефон, email или строка >5 символов [a-zA-Z0-9_])"
            logger.warning(f"Ошибка валидации логина: {msg}")
            return "False", msg

        if check_blacklist(login):
            msg = f"Логин '{login}' находится в черном списке"
            logger.warning(f"Ошибка валидации логина: {msg}")
            return "False", msg

        is_pass_valid, pass_err_code = validate_password_complexity(password)
        if not is_pass_valid:
            error_messages = {
                "PasswordTooShort": "Пароль слишком короткий (минимум 7 символов)",
                "PasswordContainsForbiddenChars": "Пароль содержит запрещенные символы (разрешены только кириллица, цифры и спецсимволы)",
                "NoUppercaseLetter": "Пароль должен содержать хотя бы одну заглавную букву (кириллица)",
                "NoLowercaseLetter": "Пароль должен содержать хотя бы одну строчную букву (кириллица)",
                "NoDigit": "Пароль должен содержать хотя бы одну цифру",
                "NoSpecialChar": "Пароль должен содержать хотя бы один спецсимвол"
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