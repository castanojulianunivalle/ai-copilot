-- Migración: agregar rol administrador
-- Ejecutar en Supabase SQL Editor si la BD ya tiene profiles con ('cliente','agente')

-- 1. Eliminar check constraint antigua y crear nueva con administrador
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_role_check;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_role_check 
  CHECK (role IN ('cliente', 'agente', 'administrador'));

-- 2. NO crear profiles_read_admin ni profiles_update_admin: provocan recursión infinita en RLS.
--    El perfil se obtiene por API (/me) con service_role. profiles_read_own basta para lectura propia.

-- 3. Actualizar políticas de tickets para incluir administrador (mismo acceso que agente)
-- Nota: si las políticas ya existen con nombres distintos, puede ser necesario recrearlas manualmente
DROP POLICY IF EXISTS "tickets_select" ON public.tickets;
CREATE POLICY "tickets_select" ON public.tickets FOR SELECT USING (
  auth.uid() IN (SELECT id FROM public.profiles WHERE role IN ('agente', 'administrador'))
  OR created_by = auth.uid() OR created_by IS NULL
);
DROP POLICY IF EXISTS "tickets_update" ON public.tickets;
CREATE POLICY "tickets_update" ON public.tickets FOR UPDATE USING (
  auth.uid() IN (SELECT id FROM public.profiles WHERE role IN ('agente', 'administrador'))
  OR (created_by = auth.uid() AND auth.uid() IN (SELECT id FROM public.profiles WHERE role = 'cliente'))
);
DROP POLICY IF EXISTS "tickets_delete" ON public.tickets;
CREATE POLICY "tickets_delete" ON public.tickets FOR DELETE USING (
  auth.uid() IN (SELECT id FROM public.profiles WHERE role IN ('agente', 'administrador'))
  OR created_by = auth.uid()
);
