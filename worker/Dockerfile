FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app /app
CMD ["celery", "-A", "worker.app.tasks", "worker", "--loglevel=info"]
