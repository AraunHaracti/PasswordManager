# app/views/json_view.py
#
# Альтернативное представление: работает через тот же PasswordManager.

from ..password_manager import PasswordManager


class JsonView:
    """
    Пример второго представления. Показывает, что ядро не привязано к консоли.
    """

    def __init__(self, manager: PasswordManager):
        self.manager = manager

    def sign_in(self, email: str, password: str) -> dict:
        return self.manager.sign_in(email, password)

    def list_passwords(self) -> dict:
        return self.manager.list_passwords()

    def create_password(self, service: str, login: str, password: str, description: str) -> dict:
        return self.manager.create_password(service, login, password, description)