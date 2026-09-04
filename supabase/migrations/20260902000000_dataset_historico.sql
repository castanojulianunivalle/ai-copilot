-- Sprint 4 · HU-08 · AISCOP-37: esquema del dataset historico
--
-- Objetivo: dejar registrado, de forma inmutable, (a) que predijo cada motor de
-- clasificacion y (b) cual era la categoria correcta segun anotacion humana.
-- Sin estas dos piezas no es posible calcular la matriz de confusion ni el
-- F1-Score del Sprint 6, ni comparar el LLM contra el motor de reglas.

-- ---------------------------------------------------------------------------
-- 1. Log de clasificaciones (una fila por prediccion, nunca se actualiza)
-- ---------------------------------------------------------------------------
-- Sirve a los dos motores: el de reglas (Semestre 1) escribe motor='reglas' y
-- el LLM (Sprint 5) escribe motor='llm'. Mantenerlos en la misma tabla evita
-- cambios de esquema al integrar la IA y permite comparar ambos con un JOIN.
create table if not exists public.classification_log (
  id           uuid primary key default gen_random_uuid(),
  ticket_id    uuid not null references public.tickets(id) on delete cascade,
  motor        text not null check (motor in ('reglas', 'llm')),
  categoria    text,
  sentimiento  text check (sentimiento in ('Frustrado', 'Urgente', 'Neutral', 'Satisfecho')),
  prioridad    text check (prioridad in ('Alta', 'Media', 'Baja')),
  confianza    numeric(4, 3) check (confianza >= 0 and confianza <= 1),
  modelo       text,
  latencia_ms  integer check (latencia_ms >= 0),
  created_at   timestamptz not null default now()
);

create index if not exists classification_log_motor_idx on public.classification_log (motor, created_at desc);

-- Una sola prediccion vigente por (ticket, motor): la re-clasificacion
-- sobreescribe en lugar de duplicar filas y sesgar las metricas.
create unique index if not exists classification_log_ticket_motor_uidx
  on public.classification_log (ticket_id, motor);

-- ---------------------------------------------------------------------------
-- 2. Etiquetas de referencia (ground truth anotado a mano)
-- ---------------------------------------------------------------------------
create table if not exists public.ticket_labels (
  ticket_id         uuid primary key references public.tickets(id) on delete cascade,
  categoria_real    text not null,
  sentimiento_real  text check (sentimiento_real in ('Frustrado', 'Urgente', 'Neutral', 'Satisfecho')),
  prioridad_real    text check (prioridad_real in ('Alta', 'Media', 'Baja')),
  anotado_por       uuid references auth.users(id) on delete set null,
  anotado_en        timestamptz not null default now(),
  notas             text
);

-- ---------------------------------------------------------------------------
-- 3. Vista de dataset
-- ---------------------------------------------------------------------------
-- El split es determinista: se deriva del uuid del ticket, no de un random().
-- Asi el mismo ticket cae siempre en la misma particion aunque se re-exporte el
-- dataset, que es lo que hace reproducible la evaluacion del Sprint 6.
-- Se comparan los dos primeros digitos hex del md5 contra 'cc' (=204/256) en
-- lugar de castear a entero: el cast bit(32)::bigint es de signo y devolveria
-- negativos para la mitad de los uuid, mandando todo el dataset a 'train'.
create or replace view public.dataset_tickets as
select
  t.id                                              as ticket_id,
  t.created_at,
  t.titulo,
  t.description,
  t.estado,
  t.category                                        as categoria_reglas_actual,
  reglas.categoria                                  as categoria_reglas,
  llm.categoria                                     as categoria_llm,
  llm.sentimiento                                   as sentimiento_llm,
  llm.prioridad                                     as prioridad_llm,
  llm.confianza                                     as confianza_llm,
  llm.modelo                                        as modelo_llm,
  llm.latencia_ms                                   as latencia_llm_ms,
  l.categoria_real,
  l.sentimiento_real,
  l.prioridad_real,
  (l.ticket_id is not null)                         as etiquetado,
  case
    when substr(md5(t.id::text), 1, 2) < 'cc' then 'train'
    else 'test'
  end                                               as split
from public.tickets t
left join public.classification_log reglas
       on reglas.ticket_id = t.id and reglas.motor = 'reglas'
left join public.classification_log llm
       on llm.ticket_id = t.id and llm.motor = 'llm'
left join public.ticket_labels l
       on l.ticket_id = t.id;

-- ---------------------------------------------------------------------------
-- 4. RLS
-- ---------------------------------------------------------------------------
-- La API escribe con service_role (que salta RLS). Estas politicas solo abren
-- lectura a agentes y administradores; el cliente final no ve el dataset.
alter table public.classification_log enable row level security;
alter table public.ticket_labels      enable row level security;

drop policy if exists "classification_log_select_staff" on public.classification_log;
create policy "classification_log_select_staff" on public.classification_log
  for select using (
    auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  );

drop policy if exists "ticket_labels_select_staff" on public.ticket_labels;
create policy "ticket_labels_select_staff" on public.ticket_labels
  for select using (
    auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  );

drop policy if exists "ticket_labels_write_staff" on public.ticket_labels;
create policy "ticket_labels_write_staff" on public.ticket_labels
  for all using (
    auth.uid() in (select id from public.profiles where role in ('agente', 'administrador'))
  );

-- ---------------------------------------------------------------------------
-- 5. Backfill del historico ya existente
-- ---------------------------------------------------------------------------
-- Los tickets creados en los Semestres 1 y 2 guardan la categoria de reglas en
-- tickets.category pero nunca pasaron por classification_log. Se rellenan aqui
-- para que la linea base cubra todo el historico y no solo lo nuevo.
insert into public.classification_log (ticket_id, motor, categoria, modelo, created_at)
select t.id, 'reglas', t.category, 'classify_with_rules@sem1', t.created_at
from public.tickets t
where t.category is not null
on conflict (ticket_id, motor) do nothing;
