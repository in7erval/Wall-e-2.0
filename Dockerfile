FROM python:latest

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN rm -rf *.jpg
COPY . /src





