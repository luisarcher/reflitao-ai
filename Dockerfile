FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use copy mode since the cache mount is not a named volume
ENV UV_LINK_MODE=copy

# Copy project metadata first for dependency layer caching
COPY pyproject.toml uv.lock README.md ./

# Copy application source
COPY reflitao/ ./reflitao/

# Install project and dependencies at system level
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

VOLUME ["/data"]

CMD ["reflitao", "/data"]
