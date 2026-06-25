FROM python:3.11-slim

WORKDIR /app

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "web_server.py"]
