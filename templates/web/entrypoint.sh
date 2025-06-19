#!/bin/bash
set -e

CERT_FILE="/etc/apache2/ssl/web.cert.pem"
KEY_FILE="/etc/apache2/ssl/web.key.pem"

# Esperamos a que los certificados estén disponibles
echo "🔍 Verificando certificados SSL..."

if [[ ! -f "$CERT_FILE" || ! -s "$CERT_FILE" ]]; then
  echo "❌ No se encontró el certificado: $CERT_FILE"
  exit 1
fi

if [[ ! -f "$KEY_FILE" || ! -s "$KEY_FILE" ]]; then
  echo "❌ No se encontró la clave privada: $KEY_FILE"
  exit 1
fi

echo "✅ Certificados encontrados. Iniciando Apache..."

# Inicia Apache en primer plano
exec apache2ctl -D FOREGROUND
