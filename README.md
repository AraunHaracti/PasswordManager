# Файл .env в корне проекта:
#   SUPABASE_URL=https://ваш-проект.supabase.co
#   SUPABASE_KEY=ваш-anon-ключ
#
# Таблица в Supabase (SQL Editor) — обновлённая схема:
#   create table passwords (
#       id bigint primary key generated always as identity,
#       user_id uuid not null references auth.users(id) on delete cascade,
#       service text not null,
#       login text not null default '',
#       description text not null default '',
#       password text not null,
#       created_at timestamptz default now(),
#       unique(user_id, service)
#   );
#
#   alter table passwords enable row level security;
#
#   create policy "Users manage own passwords"
#       on passwords for all
#       using (auth.uid() = user_id)
#       with check (auth.uid() = user_id);
#
# Запуск
# pip install -r requirements.txt
# python main.py