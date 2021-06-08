FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /tmp

COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /app
VOLUME /app

ENTRYPOINT [ "python3" ]
#ENTRYPOINT [ "gunicorn" ]

#CMD [ "api-sanic.py" ]

CMD [ "api.py" ]
#CMD [ "--socket=0.0.0.0:5000", "--protocol=http", "--cheaper-algo=busyness", "--processes 2", "--threads 8", "--need-app", "--max-requests=200", "--enable-threads", "-w wsgi:app"]
#CMD [ "--bind=0:5000", "wsgi:app"]