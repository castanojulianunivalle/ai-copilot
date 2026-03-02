-- Tabla de tickets
create extension if not exists "pgcrypto";

create table if not exists public.tickets (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  description text not null,
  category text,
  sentiment text,
  processed boolean not null default false
);

-- Realtime: asegurar payload completo en updates
alter table public.tickets replica identity full;

-- RLS
alter table public.tickets enable row level security;

-- Permitir lectura para el dashboard (anon)
create policy "tickets_read_all"
on public.tickets
for select
using (true);

-- Permitir inserción para pruebas (opcional)
create policy "tickets_insert_all"
on public.tickets
for insert
with check (true);

-- Actualizaciones se hacen con service role (RLS bypass)

-- Realtime: agregar tabla a la publicación si no existe
do $$
begin
  if not exists (
    select 1
    from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'tickets'
  ) then
    alter publication supabase_realtime add table public.tickets;
  end if;
end $$;
