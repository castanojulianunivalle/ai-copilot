# Seguridad

## No subir secretos al repositorio

- **`.env`**: Contiene tokens de ClickUp, JIRA y opcionalmente AWS. Nunca lo subas. Usa `env.example` como plantilla.
- **`cloudformation-params.json`**: Puede contener parámetros sensibles. Usa `cloudformation-params.json.example` y mantén el archivo real en local o en tu pipeline seguro.

## Uso en repos públicos

Si haces fork o clonas este repo en un repositorio público:

1. Crea tu `.env` desde `env.example` y rellena solo en tu máquina o en un gestor de secretos.
2. No ejecutes `git add .env` ni hagas commit de archivos con tokens.
3. En GitHub/GitLab, revisa que no queden credenciales en el historial; si se filtraron, revoca los tokens de inmediato.

## Reportar vulnerabilidades

Si detectas un problema de seguridad, repórtalo de forma privada (issue privado o contacto directo con los mantenedores) en lugar de abrir un issue público.
