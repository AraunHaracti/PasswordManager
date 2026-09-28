# app/password_service.py
#
# CRUD над паролями. Возвращает структурированные результаты.

from supabase import Client
from .auth_service import AuthService


class PasswordService:

    TABLE = "passwords"

    def __init__(self, client: Client, auth: AuthService):
        self.client = client
        self.auth = auth

    def _current_user_id(self):
        user = self.auth.current_user()
        return user.id if user else None

    def create(self, service: str, login: str, password: str, description: str) -> dict:
        if not service:
            return {"ok": False, "message": "Название сервиса не может быть пустым."}
        if not password:
            return {"ok": False, "message": "Пароль не может быть пустым."}

        user_id = self._current_user_id()
        if not user_id:
            return {"ok": False, "message": "Сессия истекла. Войдите заново."}

        try:
            existing = (
                self.client.table(self.TABLE)
                .select("id")
                .eq("service", service)
                .execute()
            )
            if existing.data:
                return {
                    "ok": False,
                    "message": f"Сервис '{service}' уже существует. Используйте обновление.",
                }

            self.client.table(self.TABLE).insert(
                {
                    "user_id": user_id,
                    "service": service,
                    "login": login or "",
                    "description": description or "",
                    "password": password,
                }
            ).execute()
            return {"ok": True, "message": f"Запись для '{service}' добавлена."}
        except Exception as e:
            return {"ok": False, "message": f"Ошибка добавления: {e}"}

    def read_all(self) -> dict:
        try:
            response = (
                self.client.table(self.TABLE)
                .select("service, login, description, password")
                .order("service")
                .execute()
            )
            return {"ok": True, "items": response.data or []}
        except Exception as e:
            return {"ok": False, "message": f"Ошибка чтения: {e}", "items": []}

    def read_one(self, service: str) -> dict:
        try:
            response = (
                self.client.table(self.TABLE)
                .select("service, login, description, password")
                .eq("service", service)
                .execute()
            )
            if response.data:
                return {"ok": True, "item": response.data[0]}
            return {"ok": False, "message": f"Сервис '{service}' не найден.", "item": None}
        except Exception as e:
            return {"ok": False, "message": f"Ошибка поиска: {e}", "item": None}

    def update(self, service: str, login, password, description) -> dict:
        """
        Обновляет запись. Каждый параметр, кроме service, может быть None —
        это означает «оставить текущее значение».
        """
        try:
            current = (
                self.client.table(self.TABLE)
                .select("login, description, password")
                .eq("service", service)
                .execute()
            )
            if not current.data:
                return {"ok": False, "message": f"Сервис '{service}' не найден."}

            row = current.data[0]
            payload = {
                "login": row.get("login", "") if login is None else login,
                "password": row.get("password", "") if password is None else password,
                "description": row.get("description", "") if description is None else description,
            }

            response = (
                self.client.table(self.TABLE)
                .update(payload)
                .eq("service", service)
                .execute()
            )
            if response.data:
                return {"ok": True, "message": f"Запись для '{service}' обновлена."}
            return {"ok": False, "message": f"Сервис '{service}' не найден."}
        except Exception as e:
            return {"ok": False, "message": f"Ошибка обновления: {e}"}

    def delete(self, service: str) -> dict:
        try:
            response = (
                self.client.table(self.TABLE)
                .delete()
                .eq("service", service)
                .execute()
            )
            if response.data:
                return {"ok": True, "message": f"Запись для '{service}' удалена."}
            return {"ok": False, "message": f"Сервис '{service}' не найден."}
        except Exception as e:
            return {"ok": False, "message": f"Ошибка удаления: {e}"}