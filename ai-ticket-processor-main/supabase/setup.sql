-- Mesa de Ayuda - Semestre 1 - Esquema completo con Auth (HU-01)
-- HU-02: titulo + descripcion | HU-03: estado Abierto/Cerrado | HU-04: category por reglas

create extension if not exists "pgcrypto";

-- Perfiles de usuario (rol: cliente | agente | administrador)
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'cliente' check (role in ('cliente', 'agente', 'administrador')),
  created_at timestamptz not null default now()
);

-- Trigger: crear perfil automáticamente al registrarse
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, role)
  values (new.id, 'cliente');
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Tabla de tickets
create table if not exists public.tickets (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  titulo text not null,
  description text not null,
  category text,
  estado text not null default 'Abierto' check (estado in ('Abierto', 'Cerrado')),
  created_by uuid references auth.users(id) on delete set null
);

-- Migración: agregar created_by si la tabla ya existía sin esa columna
do $$
begin
  if not exists (
    select 1 from information_schema.columns 
    where table_schema = 'public' and table_name = 'tickets' and column_name = 'created_by'
  ) then
    alter table public.tickets add column created_by uuid references auth.users(id) on delete set null;
  end if;
end $$;

-- RLS en profiles (lectura para el usuario)
alter table public.profiles enable row level security;

drop policy if exists "profiles_read_own" on public.profiles;
create policy "profiles_read_own" on public.profiles for select using (auth.uid() = id);

-- RLS en tickets
alter table public.tickets enable row level security;

-- Eliminar políticas antiguas si existen
drop policy if exists "tickets_read_all" on public.tickets;
drop policy if exists "tickets_insert_all" on public.tickets;
drop policy if exists "tickets_update_all" on public.tickets;
drop policy if exists "tickets_delete_policy" on public.tickets;

-- Cliente: ve solo sus tickets, puede insertar con created_by = auth.uid()
-- Agente: ve todos, puede actualizar cualquiera
create policy "tickets_select" on public.tickets for select using (
  auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  or created_by = auth.uid()
  or created_by is null
);

create policy "tickets_insert_cliente" on public.tickets for insert with check (
  auth.uid() in (select id from public.profiles where role = 'cliente')
  and created_by = auth.uid()
);

create policy "tickets_update" on public.tickets for update using (
  auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  or (created_by = auth.uid() and auth.uid() in (select id from public.profiles where role = 'cliente'))
);

create policy "tickets_delete" on public.tickets for delete using (
  auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  or created_by = auth.uid()
);
