# main.py
#
# Точка входа приложения. Поддерживает выбор представления:
#   python main.py            — GUI (по умолчанию)
#   python main.py --gui      — GUI
#   python main.py --console  — консольное

import argparse
import sys

from app.database import get_client
from app.password_manager import PasswordManager
from app.views.console_view import ConsoleView


def run_console(manager: PasswordManager):
    view = ConsoleView(manager)

    while True:
        logged_in = view.run_auth_flow()
        if not logged_in:
            if not view._confirm("Выйти из приложения?"):
                continue
            print("До свидания!")
            break
        view.run_crud_flow()


def run_gui(manager: PasswordManager):
    # Импорт внутри функции: если tkinter недоступен,
    # консольный режим всё равно продолжит работать.
    from app.views.gui_view import GuiView
    view = GuiView(manager)
    view.run()


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Менеджер паролей")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--gui", action="store_true", help="Запустить графическое окно (по умолчанию)")
    group.add_argument("--console", action="store_true", help="Запустить консольный режим")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    client = get_client()
    manager = PasswordManager(client)

    # При запуске приложения принудительно сбрасываем возможную сохранённую
    # сессию, чтобы пользователь всегда начинал с экрана входа.
    try:
        manager.sign_out()
    except Exception:
        pass

    if args.console:
        run_console(manager)
    else:
        run_gui(manager)


if __name__ == "__main__":
    main()