# app/password_manager.py
#
# Ядро приложения. Объединяет сервисы и предоставляет единый фасад.

from supabase import Client
from .auth_service import AuthService
from .password_service import PasswordService
from .password_generator import PasswordGenerator


class PasswordManager:
    """
    Фасад приложения. Никакой печати здесь нет — только вызовы сервисов.
    """

    def __init__(self, client: Client):
        self.client = client
        self.auth = AuthService(client)
        self.passwords = PasswordService(client, self.auth)
        self.generator = PasswordGenerator(length=20)

    # ---- аутентификация ----

    def sign_up(self, email: str, password: str) -> dict:
        return self.auth.sign_up(email, password)

    def sign_in(self, email: str, password: str) -> dict:
        return self.auth.sign_in(email, password)

    def sign_out(self) -> dict:
        return self.auth.sign_out()

    def current_user(self):
        return self.auth.current_user()

    # ---- CRUD ----
    # Порядок значений: service, login, password, description

    def create_password(self, service: str, login: str, password: str, description: str) -> dict:
        return self.passwords.create(service, login, password, description)

    def list_passwords(self) -> dict:
        return self.passwords.read_all()

    def find_password(self, service: str) -> dict:
        return self.passwords.read_one(service)

    def update_password(self, service: str, login=None, password=None, description=None) -> dict:
        return self.passwords.update(service, login, password, description)

    def delete_password(self, service: str) -> dict:
        return self.passwords.delete(service)

    # ---- генерация ----

    def generate_password(self) -> str:
        return self.generator.generate()