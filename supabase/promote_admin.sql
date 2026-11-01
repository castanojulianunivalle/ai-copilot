-- Promover primer usuario a administrador
-- Ejecutar en Supabase SQL Editor (ajustar el email al usuario deseado)
-- Ejemplo: cambiar 'admin@ejemplo.com' por el email real del primer administrador

UPDATE public.profiles
SET role = 'administrador'
WHERE id = (SELECT id FROM auth.users WHERE email = 'admin@admin.com' LIMIT 1);

-- Alternativa: promover por ID de usuario (reemplaza el UUID)
-- UPDATE public.profiles SET role = 'administrador' WHERE id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
