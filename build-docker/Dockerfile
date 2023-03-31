# Use an official Python runtime as a parent image
FROM python:3.9.0

# Set the locale to use UTF-8 encoding
ENV LANG C.UTF-8

# Copy the current directory contents into the container at /app
COPY src /app/src
COPY main.py /app/main.py
COPY input /app/input
COPY templates /app/templates
COPY schemas /app/schemas
COPY ./build-docker /app/build-docker
COPY ./build-docker/app-run.sh /app/app-run.sh

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt

RUN pip install --trusted-host pypi.python.org -r ./build-docker/requirements.txt
RUN apt-get update && apt-get install -y vim

# Replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

WORKDIR /app
CMD ["sleep", "36000"]

