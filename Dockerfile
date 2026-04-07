FROM python:3.11-slim

# 1. Copier l'exécutable uv directement depuis l'image officielle
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .

# 2. Utiliser la bonne syntaxe : "uv pip install --system"
RUN uv pip install --system --no-cache -r pyproject.toml

COPY src/ ./src/
RUN mkdir -p data/raw data/gold

CMD python src/download_data.py && \
    python src/transform_to_gold.py && \
    python src/load_to_postgres.py