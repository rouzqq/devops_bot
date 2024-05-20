FROM postgres:14

RUN apt-get update && apt-get install openssh-client openssh-server -y

ADD /init.sql /docker-entrypoint-initdb.d/