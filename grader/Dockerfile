FROM python:3.11-slim
WORKDIR /app
COPY worker.py /app/worker.py
RUN pip install docker fastapi uvicorn
ENTRYPOINT ["python", "/app/worker.py"]
