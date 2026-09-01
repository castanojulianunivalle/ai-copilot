-- Sprint 7 · HU-06b · AISCOP-31: Realtime sobre tickets
--
-- Sin esto el dashboard no recibe nada: la suscripcion del frontend se conecta
-- igual y se queda callada, que es el modo de fallo mas confuso posible.

do $$
begin
  alter publication supabase_realtime add table public.tickets;
exception
  when duplicate_object then
    raise notice 'public.tickets ya estaba en la publicacion supabase_realtime';
end $$;

-- Realtime respeta RLS, pero solo entrega la fila completa en un UPDATE o un
-- DELETE si la tabla tiene REPLICA IDENTITY FULL. Con la identidad por defecto
-- (la clave primaria) el payload de un DELETE trae unicamente el id, y el
-- dashboard no podria distinguir que ticket quitar de la lista filtrada.
alter table public.tickets replica identity full;
