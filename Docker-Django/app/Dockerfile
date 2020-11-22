# pull official base image
FROM python:3.8-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get install -y gcc g++ netcat postgresql && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip setuptools wheel
COPY ./requirements.txt .

# Fixing requiring numpy and pandas in alpine
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]