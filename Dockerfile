# Use the official Python image from the Docker Hub
FROM python:alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /current-app

# Install PDM
RUN pip install pdm

# Copy the dependency files
COPY pyproject.toml pdm.lock /current-app/

# Export dependencies to requirements.txt and install them
RUN pdm export --prod -o requirements.txt && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /current-app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
