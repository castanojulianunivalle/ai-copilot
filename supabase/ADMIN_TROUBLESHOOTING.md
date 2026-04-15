# Solución: el frontend muestra "Cliente" en lugar de "Administrador"

## Pasos para verificar y corregir

### 1. Ejecutar la migración del rol administrador (si aún no lo hiciste)

En **Supabase Dashboard → SQL Editor**, ejecuta primero:

```
supabase/migrate_admin.sql
```

Esto permite que la tabla `profiles` acepte el valor `'administrador'` en la columna `role`. Sin esto, el `UPDATE` de `promote_admin.sql` **fallará silenciosamente**.

### 2. Promover tu usuario a administrador

En **Supabase Dashboard → SQL Editor**, ejecuta:

```
supabase/promote_admin.sql
```

**Importante:** Cambia `'admin@admin.com'` por el **email exacto** con el que te registraste en la app. Si el email no coincide, el `UPDATE` no afectará ninguna fila.

### 3. Verificar en Supabase que el rol se actualizó

En **Supabase Dashboard → Table Editor → profiles**:

- Busca tu usuario por `id` (el mismo que en `auth.users`)
- Comprueba que la columna `role` diga **administrador**

### 4. Refrescar el perfil en el frontend

Tras cambiar el rol:

- Haz clic en el icono de **actualizar** (flechas circulares) junto a tu rol en el header, o
- Cierra sesión y vuelve a iniciar sesión

### 5. Comprobar la conexión a Supabase

En el archivo `frontend/.env`, revisa:

- `VITE_SUPABASE_URL` → URL de tu proyecto Supabase
- `VITE_SUPABASE_ANON_KEY` → clave anónima pública

Si el frontend apunta a otro proyecto de Supabase, los cambios en la base de datos no se reflejarán correctamente.

---

## Resumen rápido

| Síntoma                | Posible causa                     | Acción                                                 |
|------------------------|-----------------------------------|--------------------------------------------------------|
| Sigue mostrando Cliente | `migrate_admin.sql` no ejecutado | Ejecutar `migrate_admin.sql` en Supabase SQL Editor   |
| Sigue mostrando Cliente | Email en promote_admin no coincide | Cambiar el email en `promote_admin.sql` y volver a ejecutar |
| Error al cargar perfil | RLS o conexión                     | Revisar consola del navegador (F12) y variables de entorno |
