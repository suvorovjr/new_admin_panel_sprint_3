FROM --platform=linux/amd64 python:3.10.2-buster

WORKDIR /code

RUN groupadd -r web && useradd -r -g web web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y cron
RUN pip install --upgrade pip

COPY etl/requirements.txt ./

RUN pip install -r ./requirements.txt

COPY etl/ ./etl

COPY crontab /etc/cron.d/my-cron

RUN chmod 0644 /etc/cron.d/my-cron
RUN crontab /etc/cron.d/my-cron
RUN touch /var/log/cron.log

CMD ["cron", "-f"]
