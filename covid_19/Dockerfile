FROM python:3.8-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# set environment variables
ENV LAUNCHED_FROM_DOCKER_COMPOSE 0
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8050

CMD ["gunicorn","-b","0.0.0.0:8050","app:server"]