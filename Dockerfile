FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run expects the container to listen on $PORT
ENV PORT=8080
EXPOSE 8080

# We'll wrap the pipeline in a minimal Flask API for Cloud Run (Step 11b)
CMD ["python", "server.py"]