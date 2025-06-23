FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# If you have model data or static data, copy it into the container
COPY app/data/ /app/data/

EXPOSE 8001

# This Dockerfile will be used for the 'worker' service, which runs app/consumer.py
# The 'main.py' (API) can also be run for health checks or sync calls if needed.
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
# The actual command will be in docker-compose.yml
