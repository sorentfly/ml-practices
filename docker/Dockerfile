FROM python:3.12

RUN apt update && \
    apt install -y vim && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv && \
    pip install --no-cache-dir py-spy

WORKDIR /opt/app

# COPY ../build/Pipfile ../build/Pipfile.lock /opt/app/
COPY ./docker/Pipfile /opt/app

# EXPOSE 8000
# RUN pipenv --clear install --deploy --system
RUN pipenv install

COPY ./app /opt/app