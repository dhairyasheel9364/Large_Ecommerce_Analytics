# Lightweight Python image keeps the dashboard container small.
FROM python:3.10-slim

# All dashboard files will live inside /app.
WORKDIR /app

# Copy dependencies first so Docker can cache this layer.
COPY requirements.txt .

# Install dependencies without retaining pip's cache.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application.
COPY app.py .

# Document the port used by Streamlit.
EXPOSE 8501

# Start Streamlit and allow access from the host machine.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]