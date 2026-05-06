FROM ghcr.io/astral-sh/uv:latest

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY app/ ./app/

# Install project with uv
RUN uv pip install --system .

# Create non-root user for security
RUN useradd --create-home appuser
USER appuser

CMD ["app"]
