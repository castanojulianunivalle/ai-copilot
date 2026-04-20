-- Migrar base existente a Auth (Semestre 1 - HU-01)
-- Ejecutar si ya tenías tickets sin created_by

-- 1. Crear profiles si no existe
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'cliente' check (role in ('cliente', 'agente')),
  created_at timestamptz not null default now()
);

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, role)
  values (new.id, 'cliente')
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- 2. Añadir created_by a tickets
alter table public.tickets add column if not exists created_by uuid references auth.users(id) on delete set null;

-- 3. Actualizar RLS
alter table public.profiles enable row level security;
drop policy if exists "profiles_read_own" on public.profiles;
create policy "profiles_read_own" on public.profiles for select using (auth.uid() = id);

drop policy if exists "tickets_read_all" on public.tickets;
drop policy if exists "tickets_insert_all" on public.tickets;
drop policy if exists "tickets_update_all" on public.tickets;

create policy "tickets_select_by_role"
on public.tickets for select
using (
  auth.uid() in (select id from public.profiles where role = 'agente')
  or created_by = auth.uid()
);

create policy "tickets_insert_cliente"
on public.tickets for insert
with check (
  auth.uid() in (select id from public.profiles where role = 'cliente')
  and created_by = auth.uid()
);

create policy "tickets_update_by_role"
on public.tickets for update
using (
  auth.uid() in (select id from public.profiles where role = 'agente')
  or created_by = auth.uid()
);

create policy "tickets_delete_by_role"
on public.tickets for delete
using (
  auth.uid() in (select id from public.profiles where role = 'agente')
  or created_by = auth.uid()
);
