# app/views/console_view.py
#
# Консольное отображение. Работает только через PasswordManager.

from ..password_manager import PasswordManager


class ConsoleView:

    def __init__(self, manager: PasswordManager):
        self.manager = manager

    # ---------- вспомогательное ----------

    @staticmethod
    def _ask(prompt: str) -> str:
        return input(prompt).strip()

    @staticmethod
    def _ask_optional(prompt: str):
        """
        Возвращает введённое значение или None, если пользователь
        ничего не ввёл (для семантики «оставить как есть»).
        """
        raw = input(prompt).strip()
        return raw if raw != "" else None

    @staticmethod
    def _info(message: str):
        print(message)

    @staticmethod
    def _error(message: str):
        print(f"[Ошибка] {message}")

    @staticmethod
    def _success(message: str):
        print(f"[OK] {message}")

    def _confirm(self, prompt: str) -> bool:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        return answer == "y"

    # ---------- меню ----------

    def show_auth_menu(self):
        print("\n=== Менеджер паролей — Вход ===")
        print("1. Войти")
        print("2. Зарегистрироваться")
        print("0. Выход из приложения")
        print("===============================")

    def show_crud_menu(self):
        print("\n=== Менеджер паролей ===")
        print("1. Добавить запись (Create)")
        print("2. Показать все записи (Read)")
        print("3. Найти запись по сервису (Read)")
        print("4. Обновить запись (Update)")
        print("5. Удалить запись (Delete)")
        print("0. Выйти из аккаунта")
        print("========================")

    # ---------- аутентификация ----------

    def run_auth_flow(self) -> bool:
        """Возвращает True, если пользователь вошёл."""
        self.show_auth_menu()
        choice = self._ask("Выберите действие: ")

        if choice == "1":
            email = self._ask("Email: ")
            password = self._ask("Пароль: ")
            result = self.manager.sign_in(email, password)
            if result["ok"]:
                self._success(result["message"])
                return True
            self._error(result["message"])
            return False

        if choice == "2":
            email = self._ask("Email: ")
            password = self._ask("Пароль: ")
            result = self.manager.sign_up(email, password)
            if result["ok"]:
                self._success(result["message"])
                return True
            self._error(result["message"])
            return False

        if choice == "0":
            return False

        self._error("Неверный выбор.")
        return False

    # ---------- CRUD ----------

    def run_crud_flow(self):
        while True:
            self.show_crud_menu()
            choice = self._ask("Выберите действие: ")

            if choice == "1":
                self._flow_create()
            elif choice == "2":
                self._render_all()
            elif choice == "3":
                self._flow_find()
            elif choice == "4":
                self._flow_update()
            elif choice == "5":
                self._flow_delete()
            elif choice == "0":
                if self._confirm("Выйти из аккаунта?"):
                    result = self.manager.sign_out()
                    self._success(result["message"])
                    break
                else:
                    self._info("Выход отменён.")
            else:
                self._error("Неверный выбор. Попробуйте снова.")

    # ---------- сценарии CRUD ----------

    def _flow_create(self):
        # Порядок ввода: service, login, password, description
        service = self._ask("Сервис: ")
        login = self._ask("Логин: ")

        generated = self.manager.generate_password()
        self._info(f"Сгенерированный пароль: {generated}")
        edited = self._ask(
            "Нажмите Enter, чтобы принять сгенерированный пароль, "
            "или введите свой: "
        )
        password = edited if edited != "" else generated

        description = self._ask("Описание: ")

        self._print_result(
            self.manager.create_password(service, login, password, description)
        )

    def _flow_find(self):
        service = self._ask("Введите название сервиса для поиска: ")
        result = self.manager.find_password(service)
        if result["ok"]:
            self._render_item(result["item"])
        else:
            self._error(result["message"])

    def _flow_update(self):
        # Порядок ввода: service, login, password, description
        service = self._ask("Введите название сервиса для обновления: ")

        existing = self.manager.find_password(service)
        if not existing["ok"]:
            self._error(existing["message"])
            return

        self._info("Пустое поле = оставить текущее значение.")

        login = self._ask_optional("Новый логин: ")
        password = self._ask_optional("Новый пароль: ")
        description = self._ask_optional("Новое описание: ")

        if login is None and password is None and description is None:
            self._info("Ничего не изменено.")
            return

        if not self._confirm(f"Подтвердите обновление записи для '{service}'?"):
            self._info("Обновление отменено.")
            return

        self._print_result(
            self.manager.update_password(service, login, password, description)
        )

    def _flow_delete(self):
        service = self._ask("Введите название сервиса для удаления: ")
        if not self._confirm(f"Подтвердите удаление записи для '{service}'?"):
            self._info("Удаление отменено.")
            return
        self._print_result(self.manager.delete_password(service))

    # ---------- рендеринг ----------

    def _render_item(self, item: dict):
        self._info(f"  Сервис:     {item.get('service', '')}")
        self._info(f"  Логин:      {item.get('login', '')}")
        self._info(f"  Пароль:     {item.get('password', '')}")
        self._info(f"  Описание:   {item.get('description', '')}")

    def _render_all(self):
        result = self.manager.list_passwords()
        if not result["ok"]:
            self._error(result["message"])
            return
        items = result["items"]
        if not items:
            self._info("Хранилище пусто.")
            return
        self._info("\nСохранённые записи:")
        for row in items:
            self._info("-" * 40)
            self._render_item(row)

    def _print_result(self, result: dict):
        if result["ok"]:
            self._success(result["message"])
        else:
            self._error(result["message"])