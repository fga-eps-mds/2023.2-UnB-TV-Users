FROM python:3.10.9-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY  .  /app/

WORKDIR src

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]