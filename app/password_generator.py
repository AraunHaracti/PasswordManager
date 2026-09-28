# app/password_generator.py
#
# Генерация безопасных паролей.

import string
import secrets


class PasswordGenerator:
    """
    Генератор паролей на основе модуля secrets (криптостойкий источник).
    По умолчанию: длина 20, строчные + прописные + цифры + спецсимволы.
    Гарантирует наличие хотя бы одного символа из каждой категории.
    """

    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/|~"

    def __init__(self, length: int = 20):
        if length < 4:
            raise ValueError("Длина пароля должна быть не меньше 4.")
        self.length = length

    def generate(self) -> str:
        alphabet = self.LOWERCASE + self.UPPERCASE + self.DIGITS + self.SYMBOLS

        # Гарантируем по одному символу каждой категории
        required = [
            secrets.choice(self.LOWERCASE),
            secrets.choice(self.UPPERCASE),
            secrets.choice(self.DIGITS),
            secrets.choice(self.SYMBOLS),
        ]
        # Добираем остаток из общего алфавита
        rest = [secrets.choice(alphabet) for _ in range(self.length - len(required))]

        # Перемешиваем криптостойко
        chars = required + rest
        for i in range(len(chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars[i], chars[j] = chars[j], chars[i]

        return "".join(chars)