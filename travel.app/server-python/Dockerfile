FROM python:3.11-slim

WORKDIR /app

ARG CACHEBUST=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "Build time: $(date)"

ENTRYPOINT ["sh", "-c", "exec gunicorn app:app --bind 0.0.0.0:${PORT:-3000} --timeout 120"]
