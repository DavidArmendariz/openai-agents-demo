# Use the official Python image from the Docker Hub
FROM python:3.11.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /current-app

# Copy the dependency files
COPY pyproject.toml pdm.lock /current-app/

# Install PDM
RUN pip install pdm

# Export dependencies to requirements.txt
RUN pdm export --prod -o requirements.txt 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /current-app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
