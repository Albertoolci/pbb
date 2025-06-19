import requests
import json
import hashlib
import base64
from utils import *

# -----------------------------
# CERTIFICADOS Y CONFIGURACIÓN
# -----------------------------
# Rutas a tus credenciales de cliente (deben existir y ser válidas)
CLIENT_CERT = "client.crt.pem"
CLIENT_KEY = "client.key.pem"
CA_CERT = "ca.crt.pem"  # Debe ser la CA que firmó el cert del servidor (la misma que usa Istio)

# -----------------------------
# DATO A ENVIAR
# -----------------------------
data = {
    "tag": "test_tag",
    "info": "test_info"
}

# Simular la firma del contenido (esto deberías reemplazarlo por tu lógica real)
# Aquí simplemente generamos un hash y "firmamos" con base64


# Generamos hash y "firma"
hash = hashlib.sha512(f'{data['tag']}{data['info']}'.encode())
data['hash'] = hash.hexdigest()
hash_bytes = hash.digest()

signature = sign_hash(hash, 'client.key.pem')

data['signed_hash'] = signature.hex()

b = verify_hash_signature(data['signed_hash'], data['hash'], 'client.crt.pem')

if b : print('utils verified the signature')
else : print('error')


print(data)
print('Pre-conexión')

# -----------------------------
# ENVÍO AL GATEWAY
# -----------------------------
url = "https://gateway-pbb.westeurope.cloudapp.azure.com:443/"  

response = requests.post(
    url,
    json=data,
    cert=(CLIENT_CERT, CLIENT_KEY),
    verify=False
)

print(f"Status Code: {response.status_code}")
print("Response:", response.text)
