#
# usage: docker build -t nginx-ubuntu .
#
FROM ubuntu:latest

ENV TZ=America/Sao_Paulo
ARG DEBIAN_FRONTEND=noninteractive 
ENV LANG pt_BR.utf8

RUN apt-get update && \
    apt-get install -y \
    nginx \
    nano

EXPOSE 80

CMD nginx -g "daemon off;"

