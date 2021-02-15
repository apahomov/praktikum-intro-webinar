FROM python:3.9

RUN mkdir /bot \
    && groupadd -r bot --gid=1002 \
    && useradd -r -g bot --uid=1002 --home-dir=/bot/ --shell=/bin/bash bot

COPY ./requirements.bot.txt /bot/requirements.txt
RUN chown -R bot:bot /bot
WORKDIR /bot/

RUN pip install -U pip \
    && pip install -r requirements.txt

USER bot
