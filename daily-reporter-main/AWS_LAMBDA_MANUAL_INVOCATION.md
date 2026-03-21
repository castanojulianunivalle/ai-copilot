# Ejecutar Lambda Manualmente desde AWS

## Opción 1: Usando AWS CLI (Recomendado)

### Desde WSL/Linux:

```bash
# Ejecutar report1
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report1", "force_run": true}' \
    response.json

# Ejecutar report2
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report2", "force_run": true}' \
    response.json

# Ejecutar close
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "close", "force_run": true}' \
    response.json

# Ver la respuesta
cat response.json | jq

# Ver logs en tiempo real
aws logs tail /aws/lambda/daily-reporter-daily-reporter --follow --region us-east-1
```

### Con fecha específica:

```bash
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report1", "force_date": "2026-01-06", "force_run": true}' \
    response.json
```

## Opción 2: Desde AWS Console

1. Ve a **AWS Lambda** en la consola de AWS
2. Busca la función: `daily-reporter-daily-reporter`
3. Haz clic en **Test** (o crea un nuevo test event)
4. Usa este payload JSON:

```json
{
  "phase": "report1",
  "force_run": true
}
```

O para otras fases:

```json
{
  "phase": "report2",
  "force_run": true
}
```

```json
{
  "phase": "close",
  "force_run": true
}
```

5. Haz clic en **Test** para ejecutar

## Opción 3: Ver Logs

### Ver logs recientes:
```bash
aws logs tail /aws/lambda/daily-reporter-daily-reporter --region us-east-1
```

### Ver logs con seguimiento en tiempo real:
```bash
aws logs tail /aws/lambda/daily-reporter-daily-reporter --follow --region us-east-1
```

### Ver logs en AWS Console:
1. Ve a **CloudWatch** > **Log groups**
2. Busca: `/aws/lambda/daily-reporter-daily-reporter`
3. Selecciona el stream de logs más reciente

## Parámetros del Event

- `phase` (opcional): `"report1"`, `"report2"`, o `"close"`
- `force_date` (opcional): Fecha en formato `"YYYY-MM-DD"` (ej: `"2026-01-06"`)
- `force_run` (opcional): `true` para forzar ejecución incluso si no es día hábil

## Ejemplo Completo

```bash
# 1. Ejecutar report1 para una fecha específica
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report1", "force_date": "2026-01-06", "force_run": true}' \
    response.json

# 2. Ver la respuesta
cat response.json | jq

# 3. Ver logs en tiempo real
aws logs tail /aws/lambda/daily-reporter-daily-reporter --follow --region us-east-1
```

## Ejemplos Específicos: Reportes para Fechas Pasadas

### Ejecutar report1 para el 5 de enero:
```bash
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report1", "force_date": "2026-01-05", "force_run": true}' \
    response.json

cat response.json | jq
```

### Ejecutar report2 para el 5 de enero:
```bash
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report2", "force_date": "2026-01-05", "force_run": true}' \
    response.json

cat response.json | jq
```

### Ejecutar report1 para el 2 de enero:
```bash
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report1", "force_date": "2026-01-02", "force_run": true}' \
    response.json

cat response.json | jq
```

### Ejecutar report2 para el 2 de enero:
```bash
aws lambda invoke \
    --function-name daily-reporter-daily-reporter \
    --region us-east-1 \
    --payload '{"phase": "report2", "force_date": "2026-01-02", "force_run": true}' \
    response.json

cat response.json | jq
```


