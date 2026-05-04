-- Migración: esquema anterior (sentiment, processed) -> Semestre 1 (titulo, estado)
-- Ejecutar solo si ya tienes la tabla tickets con el schema antiguo

-- Agregar columnas nuevas
alter table public.tickets add column if not exists titulo text default '';
alter table public.tickets add column if not exists estado text default 'Abierto';

-- Migrar: descripción vacía -> usar description como titulo temporal
update public.tickets set titulo = left(description, 80) where titulo = '' or titulo is null;

-- Hacer titulo NOT NULL (después de migrar)
alter table public.tickets alter column titulo set not null;

-- Eliminar columnas de IA/Sem2+
alter table public.tickets drop column if exists sentiment;
alter table public.tickets drop column if exists processed;

-- Asegurar constraint de estado
alter table public.tickets drop constraint if exists tickets_estado_check;
alter table public.tickets add constraint tickets_estado_check check (estado in ('Abierto', 'Cerrado'));
