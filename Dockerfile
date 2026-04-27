FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app.py .
COPY data_store.py .
COPY pages/ ./pages/
COPY assets/ ./assets/
COPY precomputed/ ./precomputed/

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--timeout", "300", "app:server"]