from Registration import register_user


print("--- Тест 9: Нестроковый логин (None) -> exception ---")
res, msg = register_user(None, "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 10: Числовой логин (42) -> exception ---")
res, msg = register_user(42, "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 11: Список как логин -> exception ---")
res, msg = register_user(["a", "b"], "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 12: Словарь как логин -> exception ---")
res, msg = register_user({"x": 1}, "Пароль1!", "Пароль1!")
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 13: Список как пароль -> exception ---")
res, msg = register_user("new_user_ok", [1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7])
print(f"Результат: {res}, Сообщение: '{msg}'\n")


print("--- Тест 14: Словарь как пароль -> exception ---")
pwd = {"p": 1}
res, msg = register_user("new_user_ok", pwd, pwd)
print(f"Результат: {res}, Сообщение: '{msg}'\n")