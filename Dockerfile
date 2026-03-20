FROM python:3.13-slim

RUN apt-get update && apt-get install -y atftpd bash \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir flask werkzeug python-dotenv \
    && mkdir -p /dboot && chown -R nobody:nogroup /dboot

WORKDIR /app

COPY app.py /app
COPY templates/ /app/templates/
COPY static/ /app/static/

EXPOSE 69/udp
EXPOSE 5000

CMD ["bash", "-c", "atftpd --daemon --no-fork /dboot & python3 app.py"]
