# Configuración de Credenciales AWS

Este documento explica cómo configurar las credenciales de AWS para desplegar el Daily Reporter.

## Opción 1: AWS CLI Configure (Recomendado)

La forma más sencilla es usar `aws configure`:

```bash
aws configure
```

Te pedirá:
- **AWS Access Key ID**: Tu clave de acceso
- **AWS Secret Access Key**: Tu clave secreta
- **Default region name**: `us-east-1` (o la región que prefieras)
- **Default output format**: `json`

Las credenciales se guardan en:
- **Linux/Mac**: `~/.aws/credentials` y `~/.aws/config`
- **Windows**: `C:\Users\TU_USUARIO\.aws\credentials` y `C:\Users\TU_USUARIO\.aws\config`

## Opción 2: Variables de Entorno

Puedes configurar las credenciales como variables de entorno:

### Linux/Mac:

```bash
export AWS_ACCESS_KEY_ID=tu_access_key_id
export AWS_SECRET_ACCESS_KEY=tu_secret_access_key
export AWS_DEFAULT_REGION=us-east-1
```

Para hacerlo permanente, agrégalo a tu `~/.bashrc` o `~/.zshrc`:

```bash
echo 'export AWS_ACCESS_KEY_ID=tu_access_key_id' >> ~/.bashrc
echo 'export AWS_SECRET_ACCESS_KEY=tu_secret_access_key' >> ~/.bashrc
echo 'export AWS_DEFAULT_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell):

```powershell
$env:AWS_ACCESS_KEY_ID="tu_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="tu_secret_access_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

Para hacerlo permanente en PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable('AWS_ACCESS_KEY_ID', 'tu_access_key_id', 'User')
[System.Environment]::SetEnvironmentVariable('AWS_SECRET_ACCESS_KEY', 'tu_secret_access_key', 'User')
[System.Environment]::SetEnvironmentVariable('AWS_DEFAULT_REGION', 'us-east-1', 'User')
```

### Windows (CMD):

```cmd
set AWS_ACCESS_KEY_ID=tu_access_key_id
set AWS_SECRET_ACCESS_KEY=tu_secret_access_key
set AWS_DEFAULT_REGION=us-east-1
```

## Opción 3: Archivo de Credenciales Manual

Puedes crear manualmente el archivo de credenciales:

### Linux/Mac:

```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = tu_access_key_id
aws_secret_access_key = tu_secret_access_key
EOF

cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF
```

### Windows:

Crea los archivos en `C:\Users\TU_USUARIO\.aws\`:

**credentials:**
```
[default]
aws_access_key_id = tu_access_key_id
aws_secret_access_key = tu_secret_access_key
```

**config:**
```
[default]
region = us-east-1
output = json
```

## Verificar Configuración

Para verificar que las credenciales están configuradas correctamente:

```bash
aws sts get-caller-identity
```

Deberías ver algo como:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/tu-usuario"
}
```

## Obtener Credenciales AWS

Si no tienes credenciales AWS, necesitas:

1. **Crear un usuario IAM** en la consola de AWS
2. **Asignar políticas** necesarias:
   - `AWSLambda_FullAccess` (o permisos más específicos)
   - `CloudFormationFullAccess` (o permisos más específicos)
   - `AmazonS3FullAccess` (o permisos más específicos)
   - `AmazonEventBridgeFullAccess` (o permisos más específicos)
   - `IAMFullAccess` (o permisos más específicos)
3. **Crear Access Key** para el usuario
4. **Descargar las credenciales** (solo se muestran una vez)

## Permisos Mínimos Recomendados

Para mayor seguridad, crea una política IAM personalizada con solo los permisos necesarios:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "cloudformation:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket",
                "s3:CreateBucket",
                "events:*",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "iam:GetRole",
                "iam:PassRole",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## Seguridad

⚠️ **IMPORTANTE**:
- **NUNCA** subas tus credenciales a Git
- **NUNCA** compartas tus credenciales
- Usa perfiles IAM diferentes para desarrollo y producción
- Rota tus credenciales periódicamente
- Considera usar AWS SSO o roles IAM para acceso temporal

## Troubleshooting

### Error: "Unable to locate credentials"

- Verifica que las credenciales estén configuradas: `aws sts get-caller-identity`
- Verifica que el archivo `~/.aws/credentials` exista y tenga permisos correctos (600 en Linux/Mac)

### Error: "Access Denied"

- Verifica que el usuario IAM tenga los permisos necesarios
- Verifica que las credenciales no hayan expirado
- Verifica que estés usando la región correcta

### Error: "Invalid credentials"

- Verifica que las credenciales sean correctas
- Verifica que no haya espacios extra en las credenciales
- Regenera las credenciales si es necesario




