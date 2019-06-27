# se basa en una imagen
FROM python:3.7.0-alpine
# install sqlite 
RUN apk update \
    && apk add sqlite \
    && apk add socat 
# set workdirk
WORKDIR /usr/src/app
# copiamos e instalamos las dependencias
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
# copiamos app
COPY . /usr/src/x-app
# run server
CMD python manage.py run -h 0.0.0.0