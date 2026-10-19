-- Sprint 7 · HU-11 (AISCOP-67) y HU-12 (AISCOP-64).
--
-- motivo_revision: por qué un ticket va a revisión humana. Antes solo se deducía de confianza_ia ≤ 0,5;
-- ahora también cuenta un ticket urgente sin detalle del problema.
-- reclasificar: el ticket se clasificó con reglas porque el proveedor del modelo falló o limitó (HTTP 429,
-- timeout). La API lo reclasifica en segundo plano y apaga la marca.
alter table public.tickets
  add column if not exists motivo_revision text,
  add column if not exists reclasificar    boolean not null default false;

do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'tickets_motivo_revision_check') then
    alter table public.tickets add constraint tickets_motivo_revision_check
      check (motivo_revision is null or motivo_revision in ('confianza_baja', 'urgente_sin_detalle'));
  end if;
end $$;

-- Los tickets que hay que revisar o reclasificar se consultan por estas marcas.
create index if not exists tickets_motivo_revision_idx on public.tickets (motivo_revision) where motivo_revision is not null;
create index if not exists tickets_reclasificar_idx on public.tickets (created_at) where reclasificar;
