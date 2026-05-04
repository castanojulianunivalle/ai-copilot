# AISCOP-17 - Pruebas endpoint POST /create-ticket

## Endpoint
`POST /create-ticket`

## Casos de prueba

### Caso 1 - Creación exitosa (cliente autenticado)
- **Input**: `{ "titulo": "No puedo acceder", "description": "El sistema no me deja entrar" }`
- **Headers**: `Authorization: Bearer <token_cliente>`
- **Expected**: `200 OK` con `ticket_id`, `category`, `estado: "Abierto"`

### Caso 2 - Campos vacíos
- **Input**: `{ "titulo": "", "description": "" }`
- **Expected**: `400 Bad Request` - "titulo y description son requeridos"

### Caso 3 - Usuario no autenticado
- **Input**: sin token
- **Expected**: `401 Unauthorized`

### Caso 4 - Rol no cliente (agente intenta crear ticket)
- **Input**: token de agente
- **Expected**: `403 Forbidden` - "Solo clientes pueden crear tickets"

## Validaciones del endpoint
- Título y descripción obligatorios
- Solo rol `cliente` puede crear tickets (RLS + validación API)
- Estado inicial siempre `Abierto`
- `created_by` vinculado al `user_id` del token JWT
