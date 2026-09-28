# app/views/gui_view.py
#
# Графическое отображение на tkinter. Работает через PasswordManager.
#
# Особенности текущей версии:
#   - Компактный экран входа.
#   - Основное окно показывает Сервис, Логин, Пароль, Описание.
#   - Таблица растягивается на всю доступную ширину окна.
#   - Двойной клик по строке открывает отдельное окно с деталями записи.

import tkinter as tk
from tkinter import ttk, messagebox
from ..password_manager import PasswordManager


class GuiView:
    """
    GUI-представление. Открывает окно входа, после успешной
    аутентификации показывает окно управления паролями.
    """

    def __init__(self, manager: PasswordManager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("Менеджер паролей")
        self.root.geometry("760x520")
        self.root.minsize(640, 420)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TButton", padding=6)

        self.container = ttk.Frame(self.root, padding=16)
        self.container.pack(fill="both", expand=True)

        self._show_auth_screen()

    # =========================================================
    # Управление экранами
    # =========================================================

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _set_window_size(self, width: int, height: int, min_width: int, min_height: int):
        """Меняет размер окна и его минимальные габариты."""
        self.root.minsize(min_width, min_height)
        self.root.geometry(f"{width}x{height}")
        self.root.update_idletasks()

    # ---------- Экран входа ----------

    def _show_auth_screen(self):
        self._clear_container()
        self._set_window_size(width=360, height=230, min_width=340, min_height=220)

        ttk.Label(
            self.container, text="Вход", style="Header.TLabel"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        ttk.Label(self.container, text="Email:").grid(row=1, column=0, sticky="w", pady=3)
        self.email_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=self.email_var, width=26).grid(
            row=1, column=1, sticky="ew", pady=3
        )

        ttk.Label(self.container, text="Пароль:").grid(row=2, column=0, sticky="w", pady=3)
        self.password_var = tk.StringVar()
        ttk.Entry(
            self.container, textvariable=self.password_var, show="*", width=26
        ).grid(row=2, column=1, sticky="ew", pady=3)

        btns = ttk.Frame(self.container)
        btns.grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky="ew")
        ttk.Button(btns, text="Войти", command=self._on_sign_in).pack(side="left")
        ttk.Button(btns, text="Регистрация", command=self._on_sign_up).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(btns, text="Выход", command=self._on_quit).pack(side="right")

        self.container.columnconfigure(1, weight=1)

        self.root.after(50, lambda: self.root.focus_force())

    # ---------- Основной экран ----------

    def _show_main_screen(self):
        self._clear_container()
        self._set_window_size(width=760, height=520, min_width=640, min_height=420)

        header = ttk.Frame(self.container)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Мои пароли", style="Header.TLabel").pack(side="left")

        user = self.manager.current_user()
        user_label = user.email if user else ""
        ttk.Label(header, text=user_label).pack(side="right")

        toolbar = ttk.Frame(self.container)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Добавить", command=self._on_add).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Обновить", command=self._on_edit).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Удалить", command=self._on_delete).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Обновить список", command=self._reload_table).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(toolbar, text="Выйти из аккаунта", command=self._on_sign_out).pack(side="right")

        # Фрейм-обёртка для таблицы, чтобы она растягивалась на всё
        # доступное пространство контейнера.
        table_frame = ttk.Frame(self.container)
        table_frame.pack(fill="both", expand=True)

        # Колонки: Сервис, Логин, Пароль, Описание
        columns = ("service", "login", "password", "description")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=15
        )
        headings = {
            "service": "Сервис",
            "login": "Логин",
            "password": "Пароль",
            "description": "Описание",
        }
        # Стартовые ширины — пропорция, по которой tkinter будет
        # распределять дополнительное пространство (колонки stretch=True).
        widths = {"service": 180, "login": 200, "password": 200, "description": 300}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], minwidth=80, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid внутри table_frame: таблица растягивается по обеим осям.
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Двойной клик — окно деталей
        self.tree.bind("<Double-1>", self._on_row_double_click)

        self._reload_table()

    def _reload_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        result = self.manager.list_passwords()
        if not result["ok"]:
            messagebox.showerror("Ошибка", result["message"])
            return
        for item in result["items"]:
            self.tree.insert(
                "",
                "end",
                iid=item["service"],
                values=(
                    item.get("service", ""),
                    item.get("login", ""),
                    "********",
                    item.get("description", ""),
                ),
            )

    def _selected_service(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Выбор", "Сначала выберите запись в таблице.")
            return None
        return selection[0]

    # =========================================================
    # Аутентификация
    # =========================================================

    def _on_sign_in(self):
        email = self.email_var.get().strip()
        password = self.password_var.get()
        result = self.manager.sign_in(email, password)
        if result["ok"]:
            self.password_var.set("")
            self._show_main_screen()
        else:
            messagebox.showerror("Ошибка входа", result["message"])

    def _on_sign_up(self):
        email = self.email_var.get().strip()
        password = self.password_var.get()
        result = self.manager.sign_up(email, password)
        if result["ok"]:
            self.password_var.set("")
            messagebox.showinfo("Регистрация", result["message"])
            self._show_main_screen()
        else:
            messagebox.showerror("Ошибка регистрации", result["message"])

    def _on_sign_out(self):
        if not messagebox.askyesno("Подтверждение", "Выйти из аккаунта?"):
            return
        result = self.manager.sign_out()
        if result["ok"]:
            self._show_auth_screen()
        else:
            messagebox.showerror("Ошибка", result["message"])

    def _on_quit(self):
        if messagebox.askyesno("Подтверждение", "Выйти из приложения?"):
            self.root.destroy()

    # =========================================================
    # CRUD
    # =========================================================

    def _on_add(self):
        PasswordDialog(
            self.root, manager=self.manager, mode="create",
            on_success=self._reload_table,
        )

    def _on_edit(self):
        service = self._selected_service()
        if not service:
            return
        PasswordDialog(
            self.root, manager=self.manager, mode="update",
            service=service, on_success=self._reload_table,
        )

    def _on_delete(self):
        service = self._selected_service()
        if not service:
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить запись для '{service}'?"):
            return
        result = self.manager.delete_password(service)
        if result["ok"]:
            self._reload_table()
        else:
            messagebox.showerror("Ошибка", result["message"])

    # ---------- окно деталей ----------

    def _on_row_double_click(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        service = selection[0]
        DetailsWindow(
            self.root, manager=self.manager, service=service,
            on_change=self._reload_table,
        )

    # =========================================================
    # Цикл приложения
    # =========================================================

    def run(self):
        self.root.mainloop()


# =============================================================
# Диалог создания/редактирования записи
# =============================================================

class PasswordDialog:
    """
    Модальное окно для создания или обновления записи.
    Порядок полей: service, login, password, description.
    Для update пустые поля означают «оставить как есть».
    """

    def __init__(self, parent, manager: PasswordManager, mode: str,
                 service: str = None, on_success=None):
        assert mode in ("create", "update")
        self.manager = manager
        self.mode = mode
        self.service = service
        self.on_success = on_success

        self.top = tk.Toplevel(parent)
        self.top.title("Новая запись" if mode == "create" else "Редактирование записи")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)

        self._build()
        self._center(parent)

    def _center(self, parent):
        self.top.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.top.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _build(self):
        pad = {"padx": 8, "pady": 4}
        frame = ttk.Frame(self.top, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Сервис:").grid(row=0, column=0, sticky="w", **pad)
        self.service_var = tk.StringVar(value=self.service or "")
        service_entry = ttk.Entry(frame, textvariable=self.service_var, width=40)
        service_entry.grid(row=0, column=1, sticky="ew", **pad)
        if self.mode == "update":
            service_entry.state(["readonly"])

        ttk.Label(frame, text="Логин:").grid(row=1, column=0, sticky="w", **pad)
        self.login_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.login_var, width=40).grid(
            row=1, column=1, sticky="ew", **pad
        )

        ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="w", **pad)
        self.password_var = tk.StringVar()
        pwd_row = ttk.Frame(frame)
        pwd_row.grid(row=2, column=1, sticky="ew", **pad)
        ttk.Entry(pwd_row, textvariable=self.password_var, width=28).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(pwd_row, text="Сгенерировать", command=self._generate).pack(
            side="left", padx=(6, 0)
        )

        ttk.Label(frame, text="Описание:").grid(row=3, column=0, sticky="nw", **pad)
        self.description_text = tk.Text(frame, width=40, height=4, wrap="word")
        self.description_text.grid(row=3, column=1, sticky="ew", **pad)

        if self.mode == "update":
            hint = ttk.Label(
                frame,
                text="Пустые поля будут сохранены без изменений.\n"
                     "Для пароля: пусто = оставить текущий.",
                foreground="#666",
                justify="left",
            )
            hint.grid(row=4, column=0, columnspan=2, sticky="w", padx=8)

        btns = ttk.Frame(frame)
        btns.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(btns, text="Отмена", command=self.top.destroy).pack(side="right")
        ttk.Button(btns, text="Сохранить", command=self._on_save).pack(
            side="right", padx=(0, 8)
        )

        frame.columnconfigure(1, weight=1)

        if self.mode == "create":
            service_entry.focus_set()

        if self.mode == "update":
            self._load_current()

    def _load_current(self):
        result = self.manager.find_password(self.service)
        if not result["ok"]:
            messagebox.showerror("Ошибка", result["message"])
            self.top.destroy()
            return
        item = result["item"]
        self.login_var.set(item.get("login", ""))
        self.password_var.set(item.get("password", ""))
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", item.get("description", ""))

    def _generate(self):
        self.password_var.set(self.manager.generate_password())

    def _on_save(self):
        service = self.service_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get()
        description = self.description_text.get("1.0", "end").strip()

        if self.mode == "create":
            if not service:
                messagebox.showerror("Ошибка", "Название сервиса не может быть пустым.")
                return
            if not password:
                messagebox.showerror("Ошибка", "Пароль не может быть пустым.")
                return
            result = self.manager.create_password(service, login, password, description)
            if not result["ok"]:
                messagebox.showerror("Ошибка", result["message"])
                return
            self.top.destroy()
            if self.on_success:
                self.on_success()
            return

        login_arg = login if login != "" else None
        password_arg = password if password != "" else None
        description_arg = description if description != "" else None

        if login_arg is None and password_arg is None and description_arg is None:
            messagebox.showinfo("Без изменений", "Ни одно поле не изменено.")
            self.top.destroy()
            return

        if not messagebox.askyesno("Подтверждение", f"Обновить запись для '{service}'?"):
            return

        result = self.manager.update_password(
            service, login_arg, password_arg, description_arg
        )
        if not result["ok"]:
            messagebox.showerror("Ошибка", result["message"])
            return
        self.top.destroy()
        if self.on_success:
            self.on_success()


# =============================================================
# Окно деталей записи
# =============================================================

class DetailsWindow:
    """
    Отдельное окно с подробной информацией о записи.
    Пароль по умолчанию скрыт; есть кнопка «Показать/Скрыть».
    Доступны действия «Редактировать» и «Удалить».
    """

    def __init__(self, parent, manager: PasswordManager, service: str, on_change=None):
        self.manager = manager
        self.service = service
        self.on_change = on_change

        self.top = tk.Toplevel(parent)
        self.top.title(f"Запись: {service}")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)

        self._password_visible = False

        self._build()
        self._load()
        self._center(parent)

    def _center(self, parent):
        self.top.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.top.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _build(self):
        pad = {"padx": 10, "pady": 6}
        frame = ttk.Frame(self.top, padding=16)
        frame.pack(fill="both", expand=True)

        self.title_label = ttk.Label(frame, text="", style="Header.TLabel")
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(frame, text="Сервис:").grid(row=1, column=0, sticky="nw", **pad)
        self.service_var = tk.StringVar(value=self.service)
        service_entry = ttk.Entry(frame, textvariable=self.service_var, width=44)
        service_entry.grid(row=1, column=1, sticky="ew", **pad)
        service_entry.state(["readonly"])

        ttk.Label(frame, text="Логин:").grid(row=2, column=0, sticky="nw", **pad)
        self.login_var = tk.StringVar()
        login_entry = ttk.Entry(frame, textvariable=self.login_var, width=44)
        login_entry.grid(row=2, column=1, sticky="ew", **pad)
        login_entry.state(["readonly"])

        ttk.Label(frame, text="Пароль:").grid(row=3, column=0, sticky="nw", **pad)
        pwd_row = ttk.Frame(frame)
        pwd_row.grid(row=3, column=1, sticky="ew", **pad)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            pwd_row, textvariable=self.password_var, width=30, show="*"
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.toggle_btn = ttk.Button(
            pwd_row, text="Показать", width=12, command=self._toggle_password
        )
        self.toggle_btn.pack(side="left", padx=(6, 0))

        ttk.Label(frame, text="Описание:").grid(row=4, column=0, sticky="nw", **pad)
        self.description_text = tk.Text(frame, width=44, height=6, wrap="word")
        self.description_text.grid(row=4, column=1, sticky="ew", **pad)
        self.description_text.configure(state="disabled")

        btns = ttk.Frame(frame)
        btns.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(btns, text="Закрыть", command=self.top.destroy).pack(side="right")
        ttk.Button(btns, text="Удалить", command=self._on_delete).pack(
            side="right", padx=(0, 8)
        )
        ttk.Button(btns, text="Редактировать", command=self._on_edit).pack(
            side="right", padx=(0, 8)
        )

        frame.columnconfigure(1, weight=1)

    def _load(self):
        result = self.manager.find_password(self.service)
        if not result["ok"]:
            messagebox.showerror("Ошибка", result["message"])
            self.top.destroy()
            return
        item = result["item"]
        self.title_label.configure(text=f"Запись: {item.get('service', '')}")
        self.login_var.set(item.get("login", ""))
        self.password_var.set(item.get("password", ""))
        self.description_text.configure(state="normal")
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", item.get("description", ""))
        self.description_text.configure(state="disabled")
        self._password_visible = False
        self.password_entry.configure(show="*")
        self.toggle_btn.configure(text="Показать")

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="Скрыть")
        else:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="Показать")

    def _on_edit(self):
        def after_edit():
            self._load()
            if self.on_change:
                self.on_change()

        PasswordDialog(
            self.top, manager=self.manager, mode="update",
            service=self.service, on_success=after_edit,
        )

    def _on_delete(self):
        if not messagebox.askyesno(
            "Подтверждение", f"Удалить запись для '{self.service}'?"
        ):
            return
        result = self.manager.delete_password(self.service)
        if not result["ok"]:
            messagebox.showerror("Ошибка", result["message"])
            return
        self.top.destroy()
        if self.on_change:
            self.on_change()