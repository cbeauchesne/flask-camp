FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install --upgrade setuptools pip
RUN pip install -e .

RUN apt-get update && apt-get install -y nginx
RUN pip install uwsgi
COPY flask_camp/docker/nginx.conf /etc/nginx/sites-enabled/default

CMD ["/bin/bash", "flask_camp/docker/start.sh"]
