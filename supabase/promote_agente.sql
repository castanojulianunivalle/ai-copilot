-- Promover un usuario a rol 'agente' (ejecutar después de que el usuario se haya registrado)
-- Reemplaza 'email@ejemplo.com' con el email del usuario que quieres promover
UPDATE public.profiles
SET role = 'agente'
WHERE id = (SELECT id FROM auth.users WHERE email = 'email@ejemplo.com' LIMIT 1);
