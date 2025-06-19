import os
import string
import mysql.connector
import secrets

WEB_USER = 'web'
WEB_PASSWORD = os.environ['WEB_PASSWORD']
INSERTER_USER = 'inserter'
INSERTER_PASSWORD = os.environ['INSERTER_PASSWORD']
ROOT_PASSWORD = os.environ['ROOT_PASSWORD']
DATABASE_NAME = os.environ['DATABASE_NAME']
TABLE_NAME = os.environ['TABLE_NAME']
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_PORT = int(os.environ['DATABASE_PORT'])

# Conexión inicial como root
connection = mysql.connector.connect(
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user='root',
    password=ROOT_PASSWORD  # Contraseña del root
)

cursor = connection.cursor()

# Crear la base de datos si no existe
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};")

# Usar la base de datos
cursor.execute(f"USE {DATABASE_NAME};")

# Crear la tabla votos si no existe
cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        insertion_order INT AUTO_INCREMENT PRIMARY KEY,
        tag VARCHAR(100),
        info VARCHAR(100),
        insertion_time TIMESTAMP,
        client_hash CHAR(128),
        client_hash_signed TEXT,
        new_hash CHAR(128),
        new_hash_signed TEXT,
        last_hash CHAR(128)
    );
""")

# Crear un usuario con permisos restringidos
# Cambia 'inserter_user' y 'inserter_pass' por algo más seguro en producción
cursor.execute(f"CREATE USER IF NOT EXISTS '{INSERTER_USER}'@'%' IDENTIFIED BY '{INSERTER_PASSWORD}';")
cursor.execute(f"CREATE USER IF NOT EXISTS '{WEB_USER}'@'%' IDENTIFIED BY '{WEB_PASSWORD}';")

# Dar solo permisos de INSERT y SELECT
cursor.execute(f"GRANT SELECT, INSERT ON test_db.votos TO '{INSERTER_USER}'@'%';")
cursor.execute(f"GRANT SELECT ON test_db.votos TO '{WEB_USER}'@'%';")

# Aplicar los cambios
cursor.execute("FLUSH PRIVILEGES;")

print("Base de datos y usuario configurados correctamente. CRI")

connection.close()
