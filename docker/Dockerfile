FROM python:3.12

RUN apt update && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv

WORKDIR /opt/app

COPY /docker/Pipfile /docker/Pipfile.lock /opt/app
RUN pipenv --clear install --deploy --system

COPY ./app /opt/app

CMD ["tail", "-f", "/dev/null"]