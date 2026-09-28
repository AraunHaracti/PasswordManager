# app/database.py
#
# Инициализация клиента Supabase.

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Ошибка: задайте SUPABASE_URL и SUPABASE_KEY в .env")
    sys.exit(1)


def get_client() -> Client:
    """Возвращает singleton-клиент Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)