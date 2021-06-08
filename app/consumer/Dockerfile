FROM ubuntu:20.04

ENV TZ=America/Sao_Paulo
ARG DEBIAN_FRONTEND=noninteractive 
ENV LANG pt_BR.utf8

RUN apt-get update -y && \
    apt-get install -y \
    build-essential \
    python3-pip \
    python3-dev \
    libldap2-dev \
    libsasl2-dev \
    lcov \
    valgrind

WORKDIR /tmp
COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /app
VOLUME /app

ENTRYPOINT [ "python3" ]

CMD [ "consumer.py" ]
