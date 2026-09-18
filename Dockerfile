FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements/main.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY src/ /app

CMD ["python", "main.py"]
