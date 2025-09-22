FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry configuration
COPY backend/pyproject.toml backend/poetry.lock* ./

# Copy application code BEFORE installing dependencies
COPY src/ ./src/
COPY backend/.env ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies (including the current project)
RUN poetry install --only=main

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "josmoze_ecommerce.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
