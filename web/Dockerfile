FROM python:3.5.2


ENV APP /usr/src/app
WORKDIR $APP

COPY ./requirements.txt $APP

RUN pip install -r $APP/requirements.txt

COPY ./ $APP
