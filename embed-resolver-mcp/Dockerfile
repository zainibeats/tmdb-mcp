FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY embed-resolver-mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY embed_urls.py .
COPY embed-resolver-mcp/server.py .
COPY providers.json .

RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

CMD ["python", "server.py"]
