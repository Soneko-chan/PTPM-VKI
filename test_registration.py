from Registration import register_user


print("--- Тест 1: Успех ---")
res, msg = register_user("valid_user_1", "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 2: Пароли не совпадают ---")
res, msg = register_user("valid_user_1", "Пароль1!", "Пароль2!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 3: Черный список ---")
res, msg = register_user("admin", "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 4: Короткий логин ---")
res, msg = register_user("ab", "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 5: Латиница в пароле ---")
res, msg = register_user("new_user_ok", "Password1!", "Password1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 6: Нет спецсимвола ---")
res, msg = register_user("new_user_ok", "Пароль12", "Пароль12")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 7: Email ---")
res, msg = register_user("test@example.com", "Секрет9@", "Секрет9@")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 8: Телефон ---")
res, msg = register_user("+7-900-123-4567", "МойПароль1#", "МойПароль1#")
print(f"Результат: {res}, Сообщение: '{msg}'\n")