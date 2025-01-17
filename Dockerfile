FROM python:3.13-slim-bullseye
COPY . /app
WORKDIR /app
RUN python -m pip install -r requirements.txt

ARG API_HOST
ARG API_PORT
ARG API_WORKERS

ENV API_HOST=${API_HOST}
ENV API_PORT=${API_PORT}
ENV API_WORKERS=${API_WORKERS}

EXPOSE ${API_PORT}

CMD ["sh", "-c", "fastapi run --host ${API_HOST} --port ${API_PORT} --workers ${API_WORKERS}"]