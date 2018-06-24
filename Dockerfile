FROM alpine

RUN apk update
RUN apk add python3 nodejs nodejs-npm
RUN python3 -m ensurepip

ADD . /coffee

WORKDIR coffee

RUN pip3 install pipenv
RUN pipenv install
RUN npm install && npm run build

EXPOSE 5000

ENV DB_HOST=mongo
ENV FLASK_APP=coffee.py

CMD pipenv run flask run --host 0.0.0.0
