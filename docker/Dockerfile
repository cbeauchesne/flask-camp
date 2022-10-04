#
# docker build -f scripts/Dockerfile -t wiki_api .

FROM python:3.9

RUN apt-get update && apt-get install -y nginx

COPY . /app
WORKDIR /app

COPY docker/nginx.conf /etc/nginx/sites-enabled/default

RUN pip install -r requirements.txt
RUN pip install uwsgi

CMD ["/bin/bash", "docker/start.sh"]
