FROM python:3.10.6-slim
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install fastapi
RUN pip install uvicorn

COPY main.py .

CMD ["python", "main.py"]
EXPOSE 5000