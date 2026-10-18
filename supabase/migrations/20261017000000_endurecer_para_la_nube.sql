-- Sprint 6 · HU-10 · AISCOP-53: endurecimiento antes de exponer la base en la nube.
--
-- 1. dataset_tickets (Sprint 4) se creo como vista normal. Una vista normal corre
--    con los permisos de su dueno y por eso se salta RLS. En local no importaba,
--    pero en la nube la Data API publica las vistas del esquema public: cualquiera
--    con la llave anonima, que viaja dentro del frontend, podria leer todos los
--    tickets con sus etiquetas. Con security_invoker la vista respeta RLS como las
--    tablas que consulta.
alter view public.dataset_tickets set (security_invoker = true);

-- 2. Ninguna pantalla consulta datos sin sesion iniciada: el registro y el inicio
--    de sesion van a Auth, no a la Data API. El rol anonimo no necesita leer ni
--    escribir las tablas de la aplicacion; con sesion se usa el rol authenticated.
revoke all on table public.dataset_tickets    from anon;
revoke all on table public.tickets            from anon;
revoke all on table public.profiles           from anon;
revoke all on table public.classification_log from anon;
revoke all on table public.ticket_labels      from anon;
