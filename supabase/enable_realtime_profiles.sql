-- Habilitar Realtime en la tabla profiles
-- Necesario para que el frontend reciba cambios de rol en tiempo real cuando
-- un administrador modifica el rol de otro usuario.
--
-- Ejecutar en Supabase SQL Editor (puede dar error si ya está en la publicación).

ALTER PUBLICATION supabase_realtime ADD TABLE public.profiles;
