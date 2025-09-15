FROM python:3.11-slim
WORKDIR /app
COPY service.py /app/service.py
RUN pip install boto3 faiss-cpu numpy requests
ENTRYPOINT ["python", "/app/service.py"]
