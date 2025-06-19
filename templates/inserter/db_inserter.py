import datetime
import json
import ssl
import socket
import mysql
import mysql.connector
from mysql.connector import Error
from kafka import KafkaConsumer
import msgpack
import pandas
from utils import *

BUFF_SIZE = 1024
KAFKA_HOST = os.environ['KAFKA_HOST']
KAFKA_PORT = os.environ['KAFKA_PORT']
CERT_ORIGIN_PATH = os.environ['CERT_ORIGIN_PATH']
CERT_INSERTER_PATH = os.environ['CERT_INSERTER_PATH']
KEY_INSERTER_PATH = os.environ['KEY_INSERTER_PATH']
INSERTER_USER = 'inserter'
INSERTER_PASSWORD = os.environ['INSERTER_PASSWORD']
DATABASE_NAME = os.environ['DATABASE_NAME']
TABLE_NAME = os.environ['TABLE_NAME']
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_PORT = int(os.environ['DATABASE_PORT'])
print('No more root')


if __name__ == "__main__":
    # Se crea el contexto
    context = ssl.create_default_context()
    # Se carga el CA del servidor
    context.load_verify_locations(CERT_ORIGIN_PATH)
    
    # Se envuelve un socket estándar con el contexto SSL para establecer una conexión segura.
    #secure_conn = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname="localhost")

    # Se crea el consumidor Kafka
    consumer = KafkaConsumer(
        'test-kafka',  # Topic del que se lee
        bootstrap_servers=f'{KAFKA_HOST}:{KAFKA_PORT}', #Dónde está ubicada la cola Kafka
        auto_offset_reset='earliest',  # Se comienza leer desde el principio de la cola si no hay offset
        enable_auto_commit=False,  # Se deshabilita el autocommit para manejarlo manualmente y asegurar coherencia fuerte
        value_deserializer=msgpack.loads,  # Se deserializa el valor del mensaje JSON
        group_id='test-group'
    )

    print('Llega aquí')

    for message in consumer :
        try: 
            print(message.value)

            data_dict = message.value
            data_dict['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            #try :
            signed_hash = data_dict['signed_hash']
            unsigned_hash = data_dict['hash']

            if verify_hash_signature(signed_hash, unsigned_hash, CERT_ORIGIN_PATH) :
                
                # Conexión a la base de datos con TLS/SSL
                connection = mysql.connector.connect(
                    host=DATABASE_HOST,        # Dirección del servidor de base de datos
                    port=DATABASE_PORT,               # Puerto de MySQL, por defecto 3306
                    database=DATABASE_NAME,    # Nombre de la base de datos a la que quieres conectar
                    user=INSERTER_USER,       # Tu nombre de usuario de MySQL
                    password=INSERTER_PASSWORD,# Tu contraseña de MySQL
                    charset='utf8'
                    # ssl_ca='localhost.crt',           # Ruta al certificado de la CA
                    # ssl_cert='localhost.crt',     # Ruta al certificado del cliente
                    # ssl_key='localhost.key'        # Ruta a la clave del cliente
                )
                
                if connection.is_connected() :
                
                    # Crear un cursor y ejecutar una consulta
                    cursor = connection.cursor()
                    cursor.execute("SELECT DATABASE();")
                    record = cursor.fetchone()
                    print("Conectado a la base de datos: ", record)

                    print('He llegado hasta aquí')

                    # Obtener el valor last_hash del último registro basado en insertion_order
                    query = f"SELECT new_hash FROM {TABLE_NAME} ORDER BY insertion_order DESC LIMIT 1;"
                    cursor.execute(query)
                    last_hash_record = cursor.fetchone()

                    if last_hash_record is not None:
                        last_hash = last_hash_record[0]  # Extraer el valor de la primera columna (new_hash)
                        print("El valor de last_hash es:", last_hash)

                    else :
                        last_hash = None

                    if last_hash == None :
                        hash = hashlib.sha512(f'{data_dict['tag']}{data_dict['info']}{data_dict['timestamp']}{data_dict['hash']}{data_dict['signed_hash']}'.encode())
                    
                    else :
                        hash = hashlib.sha512(f'{data_dict['tag']}{data_dict['info']}{data_dict['timestamp']}{data_dict['hash']}{data_dict['signed_hash']}{last_hash}'.encode())
                    
                    data_dict['new_hash'] = hash.hexdigest()
                    
                    signature = sign_hash(hash, KEY_INSERTER_PATH)

                    data_dict['new_hash_signed'] = signature.hex()

                    print(data_dict)
                    data_dict['new_hash'] = hash.hexdigest()
                    
                    signature = sign_hash(hash, KEY_INSERTER_PATH)

                    data_dict['new_hash_signed'] = signature.hex()

                    print(data_dict)

                    # Ejecutar una consulta SQL
                    if last_hash == None :
                        sql = f"INSERT INTO {TABLE_NAME} (tag, info, insertion_time, client_hash, client_hash_signed, new_hash, new_hash_signed) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                        val = (data_dict['tag'], data_dict['info'], data_dict['timestamp'], data_dict['hash'], data_dict['signed_hash'], data_dict['new_hash'], data_dict['new_hash_signed'])
                    
                    else :
                        sql = f"INSERT INTO {TABLE_NAME} (tag, info, insertion_time, client_hash, client_hash_signed, new_hash, new_hash_signed, last_hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
                        val = (data_dict['tag'], data_dict['info'], data_dict['timestamp'], data_dict['hash'], data_dict['signed_hash'], data_dict['new_hash'], data_dict['new_hash_signed'], last_hash)
                    
                    cursor.execute(sql, val)
                    connection.commit()
                    resultados = cursor.fetchall()
                    for fila in resultados:
                        print(fila)
                    connection.close()
                

                

            #except Exception as e :
            #    print('No integrity guaranteed', e)

            # Se informa de que se ha recibido el mensaje después de su procesamiento para asegurar coherencia fuerte y la no repetición de lectura.
            consumer.commit()

        except Exception as e :
            print(e)
            # En caso de excepción no se commitea para poder volver a leer el mensaje y no perderlo.
            print(f'Error de procesamiento del mensaje.')
        
    
    # Se cierra el consumidor.
    consumer.close()