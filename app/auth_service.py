# app/auth_service.py
#
# Сервис аутентификации. Не знает ничего о UI.

from supabase import Client


class AuthService:

    def __init__(self, client: Client):
        self.client = client

    def sign_up(self, email: str, password: str) -> dict:
        if not email or not password:
            return {"ok": False, "message": "Email и пароль обязательны.", "user": None}
        try:
            response = self.client.auth.sign_up(
                {"email": email, "password": password}
            )
            if response.user is None:
                return {"ok": False, "message": "Не удалось зарегистрироваться.", "user": None}
            return {
                "ok": True,
                "message": (
                    f"Пользователь {response.user.email} зарегистрирован. "
                    "Если включено подтверждение email — проверьте почту."
                ),
                "user": response.user,
            }
        except Exception as e:
            return {"ok": False, "message": f"Ошибка регистрации: {e}", "user": None}

    def sign_in(self, email: str, password: str) -> dict:
        if not email or not password:
            return {"ok": False, "message": "Email и пароль обязательны.", "user": None}
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response.user is None:
                return {"ok": False, "message": "Неверный email или пароль.", "user": None}
            return {
                "ok": True,
                "message": f"Добро пожаловать, {response.user.email}!",
                "user": response.user,
            }
        except Exception as e:
            return {"ok": False, "message": f"Ошибка входа: {e}", "user": None}

    def sign_out(self) -> dict:
        try:
            self.client.auth.sign_out()
            return {"ok": True, "message": "Вы вышли из аккаунта."}
        except Exception as e:
            return {"ok": False, "message": f"Ошибка выхода: {e}"}

    def current_user(self):
        try:
            response = self.client.auth.get_user()
            return response.user if response else None
        except Exception:
            return None