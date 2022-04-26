FROM ubuntu:20.04

RUN apt-get update \
	&& apt-get install --yes --no-install-recommends python3 python3-pip nodejs npm \
	&& rm -rf /var/lib/apt/lists/*

ADD package.json package-lock.json pyproject.toml poetry.lock \
    webpack.config.js /coffee/

ADD templates /coffee/templates
ADD static /coffee/static

WORKDIR coffee

RUN python3 -m pip install poetry
RUN poetry install
RUN npm install && npm run build

ADD achievements.py authentication.py coffee.py config.py database.py /coffee/

EXPOSE 5000

ENV DB_HOST=mongo
ENV FLASK_APP=coffee.py

CMD poetry run flask run --host 0.0.0.0
