FROM python:3.12-slim

RUN apt-get update && apt-get install -y atftpd bash && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir flask werkzeug

RUN mkdir -p /tftpboot && chown -R nobody:nogroup /tftpboot

WORKDIR /app

COPY app.py /app

EXPOSE 69/udp
EXPOSE 5000

CMD ["bash", "-c", "atftpd --daemon --no-fork /tftpboot & python3 app.py"]
