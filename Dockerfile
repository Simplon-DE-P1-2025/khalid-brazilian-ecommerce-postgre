FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
RUN mkdir -p data/raw data/gold
CMD python src/download_data.py && \
    python src/transform_to_gold.py && \
    python src/load_to_postgres.py