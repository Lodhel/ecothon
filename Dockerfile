FROM python:3.11-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ python3-dev libssl-dev libffi-dev libsasl2-dev build-essential \
    libgl1-mesa-glx libglib2.0-0 tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


ENV TZ=Europe/Moscow


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /backend/app


RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY backend/app/ ./
