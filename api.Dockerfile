FROM python:3.9

RUN mkdir /api \
    && groupadd -r api --gid=1001 \
    && useradd -r -g api --uid=1001 --home-dir=/api/ --shell=/bin/bash api

COPY ./requirements.api.txt /api/requirements.txt
RUN chown -R api:api /api
WORKDIR /api/

RUN pip install -U pip \
    && pip install -r requirements.txt

USER api
