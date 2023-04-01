FROM python:3.10.6-slim
ADD main.py /

RUN pip install --upgrade pip
RUN pip install fastapi
RUN pip install uvicorn

COPY . .

CMD ["python", "main.py"]
EXPOSE 5000