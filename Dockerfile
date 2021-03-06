FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
COPY . /my_app/
WORKDIR /my_app
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r /var/www/requirements.txt
