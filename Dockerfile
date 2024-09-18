FROM python:3.12-alpine

RUN apk add --no-cache tzdata
ENV TZ Europe/Moscow

WORKDIR /backend/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add build-base
RUN python3 -m pip install --upgrade pip

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY .. .