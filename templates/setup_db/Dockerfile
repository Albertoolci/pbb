FROM python:3.12.4

# Establece el directorio de trabajo
WORKDIR /usr/app/src

# Copia archivos fuente y dependencias
COPY requirements.txt ./
COPY setup_db.py ./

# Instala dependencias del sistema y de Python
RUN apt-get update && \
    apt-get install -y openssl && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /usr/app/certs/inserter

CMD ["python3", "-u", "setup_db.py"]
