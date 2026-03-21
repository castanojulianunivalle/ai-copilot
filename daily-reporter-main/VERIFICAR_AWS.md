# Verificar recursos en AWS

## 1. Configurar credenciales

Si estás usando un nuevo secret key, configura las credenciales:

```bash
aws configure
```

O exporta las variables de entorno:
```bash
export AWS_ACCESS_KEY_ID="tu-access-key"
export AWS_SECRET_ACCESS_KEY="tu-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

## 2. Verificar cuenta AWS

```bash
aws sts get-caller-identity
```

**IMPORTANTE**: El Account ID debe ser `438095550710` (como aparece en el log de despliegue).
Si ves un Account ID diferente, estás en una cuenta diferente y los recursos NO estarán visibles.

## 3. Verificar recursos

### Verificar Stack de CloudFormation:
```bash
aws cloudformation describe-stacks --stack-name daily-reporter --region us-east-1
```

### Verificar función Lambda:
```bash
aws lambda get-function --function-name daily-reporter-daily-reporter --region us-east-1
```

### Verificar reglas de EventBridge:
```bash
aws events list-rules --name-prefix daily-reporter --region us-east-1
```

### Verificar bucket S3:
```bash
aws s3 ls | grep daily-reporter
```

## 4. Verificar en la consola web de AWS

1. **CloudFormation**: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks
   - Busca el stack: `daily-reporter`

2. **Lambda**: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions
   - Busca la función: `daily-reporter-daily-reporter`

3. **EventBridge**: https://console.aws.amazon.com/events/home?region=us-east-1#/rules
   - Busca las reglas que empiezan con: `daily-reporter-`

4. **S3**: https://s3.console.aws.amazon.com/s3/buckets?region=us-east-1
   - Busca el bucket: `daily-reporter-deployment-packages-438095550710`

## Problemas comunes

### Si no ves los recursos:

1. **Cuenta diferente**: Verifica que el Account ID sea `438095550710`
2. **Región incorrecta**: Asegúrate de estar en `us-east-1`
3. **Permisos insuficientes**: Necesitas permisos para ver CloudFormation, Lambda, EventBridge, S3
4. **Recursos en otra región**: Si desplegaste en otra región, cambia la región en los comandos
