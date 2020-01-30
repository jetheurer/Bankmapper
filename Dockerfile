FROM python:3.7.6-slim-buster

RUN apt-get update && apt-get install -y \
        apt-utils \
        software-properties-common \
        python3-dev \
        build-essential \
    && apt-get autoremove --purge -y software-properties-common

RUN apt-get upgrade -y

ENV WORK_DIR=/bankmapper

# this is the directory we wil work from in the docker container.
WORKDIR ${WORK_DIR}/


RUN pip install --upgrade pip
# copy all files to the docker image
COPY . ${WORK_DIR}
RUN pip install -r requirements.txt
