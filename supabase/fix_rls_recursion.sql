-- Corregir recursión infinita en políticas RLS de profiles
-- Las políticas profiles_read_admin y profiles_update_admin causan recursión porque
-- para evaluarlas hay que leer profiles, lo que vuelve a disparar las políticas.
--
-- El frontend obtiene el perfil desde la API (/me) que usa service_role.
-- La política profiles_read_own basta para que el cliente lea su propio perfil.
--
-- Ejecutar en Supabase SQL Editor.

-- Eliminar políticas que causan recursión
DROP POLICY IF EXISTS "profiles_read_admin" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_admin" ON public.profiles;

-- profiles_read_own sigue activa: los usuarios pueden leer solo su propio perfil (auth.uid() = id)
