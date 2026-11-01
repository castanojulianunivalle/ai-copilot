-- HU-07 · Dashboard analítico y reportes.
--
-- Las métricas se calculan en la base de datos: el frontend recibe solo los conteos agregados, nunca la tabla
-- completa. La función corre con los permisos de su dueño (security definer) para contar todos los tickets, así que
-- ella misma comprueba el rol: un cliente recibe un error y no puede extraer estadísticas globales.

create or replace function public.metricas_tickets(
  p_desde date default null,
  p_hasta date default null,
  p_estado text default null
) returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  v_rol text;
  v_resultado jsonb;
begin
  select role into v_rol from public.profiles where id = auth.uid();
  if v_rol is null or v_rol not in ('agente', 'administrador') then
    raise exception 'Solo agentes y administradores pueden consultar las métricas'
      using errcode = '42501';
  end if;

  with filtrados as (
    select *
    from public.tickets t
    where (p_desde is null or t.created_at >= p_desde)
      and (p_hasta is null or t.created_at < p_hasta + 1)
      and (p_estado is null or t.estado = p_estado)
  )
  select jsonb_build_object(
    'total', (select count(*) from filtrados),
    'abiertos', (select count(*) from filtrados where estado = 'Abierto'),
    'en_proceso', (select count(*) from filtrados where estado = 'En proceso'),
    'cerrados', (select count(*) from filtrados where estado = 'Cerrado'),
    'en_revision', (select count(*) from filtrados where motivo_revision is not null),
    'por_ia', (select count(*) from filtrados where clasificado_por = 'llm'),
    'confianza_media', (select round(avg(confianza_ia)::numeric, 3) from filtrados where confianza_ia is not null),
    'por_dia', coalesce((
      select jsonb_agg(jsonb_build_object('dia', dia, 'total', total) order by dia)
      from (select (created_at at time zone 'America/Bogota')::date as dia, count(*) as total
            from filtrados group by 1) d), '[]'::jsonb),
    'por_estado', coalesce((
      select jsonb_agg(jsonb_build_object('nombre', estado, 'total', total) order by total desc)
      from (select estado, count(*) as total from filtrados group by 1) e), '[]'::jsonb),
    'por_categoria', coalesce((
      select jsonb_agg(jsonb_build_object('nombre', categoria, 'total', total) order by total desc)
      from (select coalesce(category, 'Sin clasificar') as categoria, count(*) as total
            from filtrados group by 1) c), '[]'::jsonb),
    'por_prioridad', coalesce((
      select jsonb_agg(jsonb_build_object('nombre', prioridad, 'total', total) order by orden)
      from (select coalesce(prioridad, 'Sin prioridad') as prioridad, count(*) as total,
                   case prioridad when 'Alta' then 1 when 'Media' then 2 when 'Baja' then 3 else 4 end as orden
            from filtrados group by 1, 3) p), '[]'::jsonb),
    'por_sentimiento', coalesce((
      select jsonb_agg(jsonb_build_object('nombre', sentimiento, 'total', total) order by total desc)
      from (select coalesce(sentimiento, 'Sin dato') as sentimiento, count(*) as total
            from filtrados group by 1) s), '[]'::jsonb)
  ) into v_resultado;

  return v_resultado;
end;
$$;

revoke all on function public.metricas_tickets(date, date, text) from public, anon;
grant execute on function public.metricas_tickets(date, date, text) to authenticated;
