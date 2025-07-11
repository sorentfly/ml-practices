FROM python:3.12

RUN apt update && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv

WORKDIR /opt/app

COPY ./docker/Pipfile /opt/app
RUN pipenv install

COPY ./app /opt/app