FROM python:2.7-slim
MAINTAINER Nick Janetakis <nick.janetakis@gmail.com>

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

ENV INSTALL_PATH /snakeeyes
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .

CMD gunicorn -b 207.154.251.100:8000 --access-logfile - "snakeeyes.app:create_app()"
