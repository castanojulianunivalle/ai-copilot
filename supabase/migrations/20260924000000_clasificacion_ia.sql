-- Sprint 5 · HU-06 · AISCOP-43: entidades extraidas por el LLM
--
-- El detalle completo de cada prediccion vive en classification_log (Sprint 4).
-- Aqui se desnormaliza sobre `tickets` solo lo que el dashboard del agente
-- necesita pintar en cada fila, para que listar tickets no obligue a un JOIN
-- contra el log en cada carga.

alter table public.tickets
  add column if not exists sentimiento     text,
  add column if not exists prioridad       text not null default 'Media',
  add column if not exists confianza_ia    numeric(4, 3),
  add column if not exists clasificado_por text not null default 'reglas';

-- Los CHECK se agregan aparte y de forma idempotente: `add column if not
-- exists` no vuelve a aplicar la restriccion si la columna ya existia de una
-- ejecucion anterior de esta misma migracion.
do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'tickets_sentimiento_check') then
    alter table public.tickets add constraint tickets_sentimiento_check
      check (sentimiento is null or sentimiento in ('Frustrado', 'Urgente', 'Neutral', 'Satisfecho'));
  end if;

  if not exists (select 1 from pg_constraint where conname = 'tickets_prioridad_check') then
    alter table public.tickets add constraint tickets_prioridad_check
      check (prioridad in ('Alta', 'Media', 'Baja'));
  end if;

  if not exists (select 1 from pg_constraint where conname = 'tickets_confianza_ia_check') then
    alter table public.tickets add constraint tickets_confianza_ia_check
      check (confianza_ia is null or (confianza_ia >= 0 and confianza_ia <= 1));
  end if;

  if not exists (select 1 from pg_constraint where conname = 'tickets_clasificado_por_check') then
    alter table public.tickets add constraint tickets_clasificado_por_check
      check (clasificado_por in ('reglas', 'llm'));
  end if;
end $$;

-- La bandeja del agente se ordena por prioridad y luego por antiguedad (HU-09).
create index if not exists tickets_prioridad_idx
  on public.tickets (prioridad, created_at desc);

-- Cola de revision humana: prediccion de IA con confianza por debajo del umbral.
create index if not exists tickets_baja_confianza_idx
  on public.tickets (confianza_ia)
  where clasificado_por = 'llm' and confianza_ia <= 0.5;
