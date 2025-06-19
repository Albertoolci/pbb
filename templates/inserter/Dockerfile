FROM python:3.12.4

# Establece el directorio de trabajo
WORKDIR /usr/app/src

# Copia archivos fuente y dependencias
COPY requirements.txt ./
COPY db_inserter.py ./
COPY utils.py ./

# Instala dependencias del sistema y de Python
RUN apt-get update && \
    apt-get install -y openssl && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /usr/app/certs/localhost2 /usr/app/certs/inserter

# Define el punto de entrada por defecto
CMD ["python3", "-u", "db_inserter.py"]
