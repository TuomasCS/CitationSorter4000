FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/TuomasCS/CitationSorter4000"
LABEL org.opencontainers.image.description="Citation sorter"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY src ./src

EXPOSE 5000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["flask", "--app", "src.app", "run", "--host=0.0.0.0", "--port=5000"]