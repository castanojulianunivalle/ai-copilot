-- Sprint 7 · HU-13: atención de tickets por agentes.
--
-- Hasta v2.1.0 la cola era compartida y sin dueño: cualquier agente cambiaba el estado de cualquier ticket y no
-- quedaba rastro de quién lo hizo. Esta migración agrega:
--   1. El estado intermedio «En proceso», para que el cliente sepa que alguien ya está trabajando su caso.
--   2. La asignación: asignado_a apunta al agente que tomó el ticket.
--   3. El correo en profiles, para mostrar quién atiende sin consultar la API de administración de Auth.
--   4. ticket_eventos: comentarios, cambios de estado y de asignación, con su autor. Un comentario puede ser una
--      nota interna, visible solo para agentes.
-- Todo es aditivo: v2.1.0 sigue funcionando sobre la base migrada.

-- 1. Estado intermedio
alter table public.tickets drop constraint if exists tickets_estado_check;
alter table public.tickets add constraint tickets_estado_check check (estado in ('Abierto', 'En proceso', 'Cerrado'));

-- 2. Asignación
alter table public.tickets
  add column if not exists asignado_a  uuid references public.profiles(id) on delete set null,
  add column if not exists asignado_en timestamptz;
create index if not exists tickets_asignado_a_idx on public.tickets (asignado_a) where asignado_a is not null;

-- 3. Correo en profiles: el trigger lo copia al registrarse y los perfiles existentes se completan desde Auth.
alter table public.profiles add column if not exists email text;
update public.profiles p set email = u.email from auth.users u where u.id = p.id and p.email is null;

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, role, email)
  values (new.id, 'cliente', new.email)
  on conflict (id) do update set email = excluded.email;
  return new;
end;
$$ language plpgsql security definer set search_path = public;

-- 4. Historial del ticket
create table if not exists public.ticket_eventos (
  id             uuid primary key default gen_random_uuid(),
  ticket_id      uuid not null references public.tickets(id) on delete cascade,
  autor_id       uuid references public.profiles(id) on delete set null,
  tipo           text not null check (tipo in ('comentario', 'estado', 'asignacion')),
  texto          text,
  interno        boolean not null default false,
  estado_antes   text,
  estado_despues text,
  asignado_antes   uuid,
  asignado_despues uuid,
  created_at     timestamptz not null default now()
);
create index if not exists ticket_eventos_ticket_idx on public.ticket_eventos (ticket_id, created_at);

-- La API escribe con service_role. Para leer directo desde el frontend: los agentes ven todo; el cliente ve los
-- eventos de sus tickets que no son notas internas.
alter table public.ticket_eventos enable row level security;
drop policy if exists "ticket_eventos_select" on public.ticket_eventos;
create policy "ticket_eventos_select" on public.ticket_eventos for select using (
  auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  or (not interno and ticket_id in (select id from public.tickets where created_by = auth.uid()))
);
revoke all on table public.ticket_eventos from anon;
