FROM python:3.12.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/retinacelltwin

COPY requirements-lock.txt ./
RUN python -m pip install --no-cache-dir --requirement requirements-lock.txt

COPY . .

CMD ["./run_verification.sh"]
