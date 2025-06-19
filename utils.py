import hashlib
import ssl
import socket
import os
import csv
import struct
import pandas
import json
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


BUFF_SIZE = 1024

def send_file(s: ssl.SSLSocket, filename:str) -> None :
    """
    Envía un archivo a través de un socket TLS previamente creado y emparejado.

    Se obtiene el tamaño del archivo a enviar y se informa de ello al destinatario.

    A continuación, se envía en paquetes de 1024 bytes hasta que se ha enviado al completo.
    
    @type s: ssl.SSLSocket
    @param s (SSLSocket): socket TLS a través del cual se va a enviar el archivo
    @type filename: str
    @param filename: ruta del archivo que se desea enviar.
    """

    # Se obtiene el tamaño del archivo a enviar.
    size = os.path.getsize(filename)
    print(f'Size = {size}')

    # Se informa al servidor del tamaño del archivo que se va a enviar.
    s.sendall(struct.pack("<Q", size))

    # Se envia el archivo en bloques de 1024 bytes.
    with open(filename, 'rb') as file :
        while read_bytes := file.read(BUFF_SIZE) :
            print(f'Envío: {read_bytes}')
            s.sendall(read_bytes)

    s.shutdown(socket.SHUT_WR)  # Cierra el lado de escritura del socket

def receive_file_size(s: ssl.SSLSocket) -> int :
    """
    Recibe el tamañno del archivo que se desea recibir a través de un socket TLS previamente creado y emparejado.
    
    @type s: ssl.SSLSocket
    @param s: socket TLS a través del cual se va a recibir el tamaño del archivo.
    @rtype: int
    @return: Tamaño del archivo que se va a recibir.
    """

    fmt = '<Q'
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()

    while received_bytes < expected_bytes :
        chunk = s.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    
    filesize = struct.unpack(fmt, stream) [0]
    print(f'Size = {filesize}')
    return int(filesize)

def receive_file(s: ssl.SSLSocket, filename:str) -> None:
    """
    Recibe un archivo a través de un socket TLS previamente creado y emparejado.

    Se llama a receive_file_size(s) para obtener el tamaño del archivo a recibir y a continuación
    se abre un nuevo archivo en el directorio actual con el contenido de lo recibido.
    
    @type s: ssl.SSLSocket
    @param s: socket TLS a través del cual se va a recibir el archivo.
    @type filename: str
    @param filename: nombre que se le quiere poner al archivo recibido.

    @raise RuntimeError: se lanza una excepción cuando se ha roto la conexión del socket y no se ha podido recibir correctamente el archivo.
    """
    #Se lee la cantidad de bytes que se van a recibir.
    filesize = receive_file_size(s)
    print(f'Utils filesize = {filesize}')

    # new_filename = f'{filename[0:-5]}2.json'

    #Se abre un nuevo archivo donde se van a guardar los datos recibidos.
    with open(filename, 'wb') as file :
        #Se reciben los datos en bloques de 1024 bytes.
        received_bytes = 0

        while received_bytes < filesize :
            chunk = s.recv(BUFF_SIZE)
            print(chunk)
            if chunk == b'':
                raise RuntimeError("socket connection broken")

            if chunk :
                file.write(chunk)
                received_bytes += len(chunk)

def read_json(filename:str) :
    """
    Recibe una ruta a un archivo json y devuelve su contenido en una lista de formato json.
    
    @type filename: str
    @param filename: ruta del archivo json que se desea leer.
    @rtype: dict
    @return: el contenido del archivo en formato JSON
    """
    
    with open(filename, 'r') as file :
        data = json.load(file)
    return data

def extract_public_key_from_certificate(filename:str) :
    """
    Recibe la ruta de un archivo .crt y devuelve la clave pública que contiene.
    
    @type filename: str
    @param filename: ruta del archivo .crt del que se desea extaer la clave pública
    @return: la clave pública"""
    # Se lee el certificado .crt desde el archivo
    with open(filename, "rb") as cert_file:
        # Se carga el certificado en formato PEM o DER según el formato del archivo
        cert_data = cert_file.read()

        try:
            # Intentar cargar como PEM
            certificate = load_pem_x509_certificate(cert_data)

        except ValueError:
            # Si no es PEM, intentar cargar como DER
            certificate = load_der_x509_certificate(cert_data)

        # Se extrae la clave pública del certificado
        public_key = certificate.public_key()
        return public_key

def verify_hash_signature(signed_hash:str, unsigned_hash:str, certificate:str) -> bool:
    """
    Recibe un hash firmado, el hash sin firmar y un certificado y si el hash firmado proviene de la firma del hash no firmado con la clave privada correspondiente al certificado
    
    @type signed_hash: str
    @param signed_hash: hash firmado
    @type unsigned_hash: str
    @param unsigned_hash: hash no firmado
    @type certificate: str
    @param certificate: ruta del certificado
    @return: True si el hash firmado proviene de la firma del hash no firmado con la clave privada correspondiente al certificado proporcionado

    @raise Exception: la firma no es válida.
    """

    try :
        public_key = extract_public_key_from_certificate(certificate)
        public_key.verify(
            bytes.fromhex(signed_hash),
            bytes.fromhex(unsigned_hash),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )

        return True
        
    except Exception as e:
        raise e
    
def sign_hash(hash, private_key_path:str) -> bytes :
    """
    Recibe un hash y la ruta de un archivo conteniendo una clave privada y devuelve el hash firmado.
    
    @type hash: _Hash
    @type private_key_path: str
    @rtype: bytes
    @return: hash firmado con la clave privada proporcionada
    """

    # Se lee la clave privada
    with open(private_key_path, 'rb') as file :
        private_key = load_pem_private_key(file.read(), password=None)

    signature = private_key.sign(
            hash.digest(), 
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )
    return signature
