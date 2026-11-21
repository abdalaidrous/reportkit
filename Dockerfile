# ReportKit with PDF export: Python, WeasyPrint system libraries (Pango) and Arabic/Latin fonts.
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-noto-core fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install -e ".[pdf]"

COPY . .

CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"]
