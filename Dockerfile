FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
COPY apps ./apps

RUN uv sync --locked --group dev --no-editable --no-cache

EXPOSE 8080

CMD ["sh", "-c", "uv run --no-sync streamlit run apps/streamlit/lab.py --server.address=0.0.0.0 --server.port=${PORT:-8080}"]
