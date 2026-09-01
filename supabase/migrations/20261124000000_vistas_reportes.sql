-- Sprint 8 · HU-07 · AISCOP-33: vistas agregadas para el dashboard analitico
--
-- La agregacion se hace en la base y no en la API: traerse todos los tickets a
-- Python para contarlos alli obliga a paginar por PostgREST y a mantener dos
-- definiciones de cada metrica. Aqui hay una sola.

-- ---------------------------------------------------------------------------
-- Resumen general (una fila)
-- ---------------------------------------------------------------------------
create or replace view public.reportes_resumen as
select
  count(*)                                                        as total,
  count(*) filter (where estado = 'Abierto')                      as abiertos,
  count(*) filter (where estado = 'Cerrado')                      as cerrados,
  count(*) filter (where prioridad = 'Alta')                      as prioridad_alta,
  count(*) filter (where prioridad = 'Alta' and estado = 'Abierto') as alta_sin_resolver,
  count(*) filter (where clasificado_por = 'llm')                 as clasificados_ia,
  count(*) filter (where clasificado_por = 'llm' and confianza_ia <= 0.5) as requieren_revision,
  count(*) filter (where sentimiento in ('Frustrado', 'Urgente'))  as tono_negativo,
  round(avg(confianza_ia) filter (where clasificado_por = 'llm'), 3) as confianza_media_ia,
  -- Tasa de resolucion en porcentaje. El NULLIF evita la division por cero
  -- cuando todavia no hay ningun ticket.
  round(
    100.0 * count(*) filter (where estado = 'Cerrado') / nullif(count(*), 0), 1
  )                                                               as tasa_resolucion
from public.tickets;

-- ---------------------------------------------------------------------------
-- Desglose por categoria
-- ---------------------------------------------------------------------------
create or replace view public.reportes_por_categoria as
select
  coalesce(category, 'Sin clasificar')                            as categoria,
  count(*)                                                        as total,
  count(*) filter (where estado = 'Abierto')                      as abiertos,
  count(*) filter (where estado = 'Cerrado')                      as cerrados,
  count(*) filter (where prioridad = 'Alta')                      as prioridad_alta,
  round(avg(confianza_ia) filter (where clasificado_por = 'llm'), 3) as confianza_media_ia
from public.tickets
group by 1
order by 2 desc;

-- ---------------------------------------------------------------------------
-- Serie diaria de los ultimos 90 dias
-- ---------------------------------------------------------------------------
-- Se genera la serie de fechas y se hace LEFT JOIN para que los dias sin
-- tickets aparezcan con cero. Sin eso la grafica une el 3 con el 7 con una
-- recta y sugiere una actividad que no hubo.
create or replace view public.reportes_serie_diaria as
select
  dias.dia::date                                                  as dia,
  count(t.id)                                                     as creados,
  count(t.id) filter (where t.estado = 'Cerrado')                 as cerrados,
  count(t.id) filter (where t.prioridad = 'Alta')                 as prioridad_alta
from generate_series(
       (current_date - interval '89 days'), current_date, interval '1 day'
     ) as dias(dia)
left join public.tickets t
       on t.created_at >= dias.dia
      and t.created_at <  dias.dia + interval '1 day'
group by 1
order by 1;

-- ---------------------------------------------------------------------------
-- Desglose por sentimiento
-- ---------------------------------------------------------------------------
create or replace view public.reportes_por_sentimiento as
select
  coalesce(sentimiento, 'Sin analizar')                           as sentimiento,
  count(*)                                                        as total,
  count(*) filter (where estado = 'Abierto')                      as abiertos
from public.tickets
group by 1
order by 2 desc;

-- ---------------------------------------------------------------------------
-- IA vs motor de reglas, en produccion
-- ---------------------------------------------------------------------------
-- Complementa la evaluacion offline del Sprint 6: alli se mide contra ground
-- truth sobre un conjunto fijo; aqui se mide cuanto se separan los dos motores
-- sobre el trafico real. No dice quien acierta —no hay etiqueta— pero si en que
-- categorias discrepan, que es donde conviene anotar mas tickets.
create or replace view public.reportes_ia_vs_reglas as
select
  reglas.categoria                                                as categoria_reglas,
  llm.categoria                                                   as categoria_llm,
  count(*)                                                        as total,
  round(avg(llm.confianza), 3)                                    as confianza_media
from public.classification_log reglas
join public.classification_log llm
  on llm.ticket_id = reglas.ticket_id
 and llm.motor = 'llm'
where reglas.motor = 'reglas'
group by 1, 2
order by 3 desc;
