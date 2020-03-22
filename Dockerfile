FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano tree
RUN pip install -r /var/www/requirements.txt
