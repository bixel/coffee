FROM continuumio/miniconda3

RUN apt-get update -qq \
    && curl -sL https://deb.nodesource.com/setup_7.x | bash - \
    && apt-get install -y nodejs

ADD . /coffee

WORKDIR coffee

RUN pip install -r requirements.txt
RUN npm install && npm run build

EXPOSE 5000

ENV COFFEE_SERVER=0.0.0.0
ENV COFFEE_DB=/data/coffee.db

CMD python coffee.py
