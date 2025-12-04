FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install agentready
RUN pip install --no-cache-dir -e .

# Set entrypoint
ENTRYPOINT ["agentready"]
CMD ["--help"]
