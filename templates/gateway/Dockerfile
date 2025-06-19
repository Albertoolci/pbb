FROM python:3.12.4

WORKDIR /usr/app/src

COPY requirements.txt ./
COPY utils.py ./
COPY gateway.py ./

RUN apt-get update && apt-get install -y openssl
RUN pip install --no-cache-dir -r requirements.txt
RUN ls -la /usr/app/src
WORKDIR /usr/app
RUN mkdir certs
RUN cd certs
RUN mkdir client
WORKDIR /usr/app/src
EXPOSE 8080

CMD ["python", "-u", "gateway.py"]