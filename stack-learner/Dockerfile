# FROM python:3.8.12-slim-buster
FROM --platform=linux/arm64 python:3.8.12-slim-buster

# RUN pip install tensorflow

RUN mkdir /app
WORKDIR /app

COPY src /app/

# RUN apk add build-base libffi-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 19020

# ws
EXPOSE 8765

ENTRYPOINT [ "python3", "main.py" ]