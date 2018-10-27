FROM cs-base

MAINTAINER Jeff Kenney

COPY . /app

WORKDIR /app

CMD python3 client.py
