from flask import Flask, request, jsonify
from kafka import KafkaProducer
from utils import verify_hash_signature, extract_public_key_from_certificate
import os
import json
import msgpack

app = Flask(__name__)

CLIENT_CERT_PATH = os.environ.get("CLIENT_CERT_PATH")  # Para verificar firma

KAFKA_HOST = os.environ.get("KAFKA_HOST")
KAFKA_PORT = os.environ.get("KAFKA_PORT")
LISTEN_PORT = os.environ.get("LISTEN_PORT", "8080")

producer = KafkaProducer(
    value_serializer=msgpack.dumps,
    bootstrap_servers=[f'{KAFKA_HOST}:{KAFKA_PORT}'],
    retries=5
)

@app.route("/", methods=["POST"])
def handle_json():
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        # Verificar firma con el certificado del cliente
        if verify_hash_signature(data['signed_hash'], data['hash'], CLIENT_CERT_PATH):
            producer.send('test-kafka', data)
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "signature invalid"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(LISTEN_PORT)
    )
