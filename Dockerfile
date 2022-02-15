FROM python:latest

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r requirements.txt
RUN rm -rf *.jpg
RUN rm -rf temp_images/*.jpg
COPY . /src





